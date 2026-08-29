# business_operations.board-governance — lab notes (template row)

**Depth: J-DEPTH.** Deepened 2026-08-25 from a GIST draft. The `.json` was already substantial and
is **preserved almost entirely**; this pass verified it, argued the three legs it had only asserted,
added the reciprocal seams the dispatch named, and made two structural additions to the JSON. The
"what changed in this pass" section at the end is the audit trail.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the only source quoted. **27 distinct quotations** are
  used across the memo and the JSON; every one was machine-verified against `00` before this file was
  returned. No paraphrase is presented as a quote. Quotations of *neighbour catalogue files* are
  separately marked as such in the prose and were verified against those files, not against `00`.
- `planning/domains/_CONTRACT.md` — entry shape; rules 10 and 15 (a dimension may only branch on a
  field the same entry's schema declares) are what force `dimension_order: []`.
- `planning/domains/CONNECTION.md` — §2 (the node test), §4 step 2 (activation), §5 invariant 2
  (`file_kind_plausible` is constitutionally never-alone), §9 failure mode 6 (a residual duplicating
  a template without a fallthrough), PR-6 (a field-less schema's templates write no field rows).
- `planning/domains/CONNECTION-EXAMPLES.md` fixture 5 — the `.ics` fixture: a calendar file is a
  `SOURCE_TYPE`, never a domain.
- `planning/domains/canonical_fields.json` — checked so that this row mints nothing.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked; the nine this row lists are all in it.
- `planning/domains/ROSTER.md` Appendix A line 806 — the legacy id absorbed: `ops.board-governance`
  (ROW). This row owns that coverage and no more.

### The schema anchor, read first and used as the measuring stick

`planning/domains/nodes/business_operations.research.md` (J-DEPTH, 46KB). Two things in it are
binding on this row and are applied explicitly below:

1. **The default template paragraph the 24 siblings must differ from:** *the organisational unit or
   entity only where the corpus genuinely spans more than one → the governance body, project,
   contract, or account the material belongs to → the fiscal period → the document function. Not
   time-first.* Note that the anchor's second level **names "governance body" first among its four
   examples**. That is a hazard for this row, not a gift, and §"Leg 1" below treats it as one.
2. **The never-alone principle generalised for all 24 siblings:** *No sibling may rest its
   activation on an entity name, a business vocabulary word, or a document shape alone. Each of the
   three is never-alone here. Every detection signal a sibling writes must pair a **structure** with
   a **labelled slot**.* §"Applying the family's never-alone principle" audits this row's eight
   deterministic signals against that rule, one by one. It is the most useful thing this pass did.

### Landed neighbours read before writing (and not touched)

- `business_operations.organisational-records.json` — **the family's refusal, and read first, as the
  dispatch instructed.** It is this row's nearest danger and it is treated as such throughout.
- `business_operations.meeting-record.json` — the sibling being deepened in parallel. Read in full
  and **not edited**. Its side of our shared boundary is quoted below and this row's side is written
  to agree with it, not to overwrite it.
- `business_operations.corporate-regulatory-filings.json` — read in full, including all nine of its
  `collides_with` entries.
- `finance.cap-table-equity.json` (landed launch row, full depth) — read in full. It supplies the
  **same-bytes fixture** for the equity seam.
- `construction_property.agency-listing.research.md` — read for its leg-3 method, on the dispatch's
  instruction. Not a neighbour of this row; a methodological source, and the debt is acknowledged.

---

## Provenance: why this row is `proposal` and `design_cite` is `null`

`00` does not name a board, a committee, a quorum, a resolution or a company secretary anywhere.
Every claim below about what this world files is therefore either (a) a named real document type,
(b) an argued inference explicitly marked as one, or (c) a quotation from `00` used for a *general*
rule that this row then applies. The row claims no design mandate and its `design_cite` stays
`null`. Where a `00` sentence is written about a different subject — the university-name sentence is
written about a university — the read-across is labelled as inference in both the memo and the JSON.

---

## What this row is for, and what it holds

The recurring cycle of a **constituted body** — a board of directors, a board committee (audit,
remuneration, nomination, risk), a trustee body, a members' or shareholders' meeting — running under
terms of reference and producing a decision record that **has standing outside the room**.

Named real document types it holds:

- **Notice of meeting** and convening papers (the cycle's opening artifact).
- **The pack**: a cover page, a numbered index of papers with for-decision / for-noting markers, and
  the individual **board papers** behind it, each with an author or sponsor.
- **Minutes**, in their two states — draft and approved-at-the-next-meeting. The two states are a
  `version_family` relation, which is a *universal* fact, not this row's own.
- **Written (circular) resolutions** — passed without a meeting, so they carry a recital block and an
  operative clause but **no agenda and no attendance list at all**.
- **Attendance and quorum records**; **conflict-of-interest declarations and registers**.
- **Terms of reference**, **schedules of matters reserved**, **delegated-authority matrices** (a
  table of decision types against approval levels and monetary thresholds).
- **Statutory register extracts** (directors, members, PSC), **proxy and poll records**.
- **Board evaluation / effectiveness reviews**; the chair's and secretary's correspondence.

The anchor is **the body and its cycle** — not any one meeting, and not any one topic. That single
sentence is what the whole node test turns on, and it is what the gist draft got right.

---

## The node test, argued leg by leg

CONNECTION §2: a template row exists **only** when its detection signals, its recommended dimensions,
**or** its privacy rules differ from its schema's default template. One leg suffices. This row has
two, and **fails the third outright** — the failure is conceded rather than argued around.

### Leg 1 — recommended dimensions. **Fails. Conceded, and it must be conceded.**

`template.dimension_order` is `[]` and cannot be otherwise: `_CONTRACT` rules 10 and 15 permit a
dimension only on a field the same entry's schema declares, and `business_operations` declares none
(D1's deferral stands; CONNECTION PR-6). So the dimensions leg is **unavailable to all 24 siblings
equally** and can distinguish none of them. Any sibling that claims it is claiming something the
contract does not let it have.

There is a sharper hazard here than the generic one, and this is where the gist draft was thin. The
schema anchor's default paragraph names **"the governance body"** as the *first* of the four
examples at its second level. It would be very easy to read that as "the anchor already recommends
this row's shape, therefore this row's shape differs from the default" — which is backwards. It
means the opposite: **this row's preferred shape is literally the family default's own example.** If
the dimensions leg were available, this row would be the sibling *least* able to claim it.

The row's prose recommendation is recorded in `template.why` anyway, for whoever answers the schema
row's open question: **body → meeting occurrence or cycle → document function**, with an entity level
only where the corpus genuinely spans more than one entity, and **never time-first**. Three `00`
sentences constrain that prose and all three are quoted in the JSON: *"A folder should not become a
collection point for everything produced by the same person or organization."*; *"For document and
record domains, project, function, or subject usually comes before time because putting year first
scatters related work across calendar folders."*; and *"The system recommends an order based on the
domain template, but the user can reverse, remove, add, or flatten dimensions."* The anchor's warning
that a governance year is a **content** period and not a capture date — so no sibling in this family
may claim `00`'s time-first exception, which is granted to capture-based media only — is honoured:
`time_first` is `false`.

**Verdict on leg 1: fails.**

### Leg 2 — detection signals. **Passes, and it is this row's strongest leg.**

The family default has no *structure* of its own; it is what activates when the schema is plausible
and no sibling situation fires. This row has five structures that no other sibling in the family
produces, and each one pairs a structure with a labelled slot, as the anchor's principle demands:

- **The convening structure.** A named body + a meeting date and time + a venue or dial-in + *either*
  a quorum statement *or* a notice-period statement. No other document in this family is a notice of
  a future meeting of a constituted body. `meeting-record`'s recurring team sync produces a calendar
  invitation, not a notice with a notice period.
- **The numbered papers index.** A cover page naming body and date, then a numbered index of papers,
  each item naming an author or sponsor **and carrying a decision-or-noting marker.** This is the
  single most discriminating structure the row has. A team deck has no paper numbering and no
  noting/decision column; a project status pack has neither; a policy handbook has neither.
- **The minute structure.** Attendance and apologies, numbered items matching a prior agenda, a
  resolution block with proposer and seconder or an agreed-by line, and an actions table. Only the
  *last* of those four is shared with `meeting-record` — which is exactly why the actions table alone
  is not allowed to fire this row. `00` on why the table matters at all: *"Tables matter because
  resumes, forms, applications, invoices, and administrative documents often place their most useful
  information in cells rather than body paragraphs."*
- **The written-resolution structure.** A title naming a resolution of a named body, a recital block,
  an operative `IT WAS RESOLVED` clause, and a circulation/signature block — **with no agenda and no
  attendance.** This one is decisive on its own terms: it is a governance artifact that fails every
  *meeting*-shaped test, which proves the row's anchor is the body and not the meeting.
- **The governing-instrument structure.** Terms of reference, a schedule of matters reserved, a
  delegated-authority matrix — decision types against approval levels and monetary thresholds, with a
  review date. This is the body's own constitution.

None of these is a *vocabulary* claim. The words "board", "minutes", "resolution" and "quorum" are
explicitly demoted to `never_alone` in the JSON, for the reason argued in the next section. The
signals are structural, and each names the labelled slot that carries them.

**Verdict on leg 2: passes.**

### Leg 3 — privacy rules. **Passes, and the dispatch was right to make this the row's warning.**

The dispatch asked whether board material warrants a **stricter** posture than the schema default.
Following the `agency-listing` method, the first job is to establish which direction the error runs
in, because the expensive mistake is reasoning about a privacy posture the *wrong way round*.

**The available wrong direction here is the reverse of `agency-listing`'s, and it is seductive.** It
runs: *board minutes are the most formal, most lawyered, most deliberately-worded documents an
organisation produces; they are drafted for circulation, approved by a vote, and in a listed company
parts of them are announced to a market. Therefore they are the family's least casual and least risky
material — certainly less exposed than an informal one-to-one note, which the sibling
`meeting-record` correctly calls "the least ceremonial documents an organisation produces and, for
that reason, the least guarded."* That argument is wrong, and it is wrong in an instructive way:
**formality is a property of the drafting, not of the exposure.** A document being carefully worded
tells you nothing about whose secrets are inside it.

There is a second wrong direction, the exact analogue of the one `agency-listing` caught: *a listed
company publishes its AGM notice, its annual report and its governance statement, so this row's
material is substantially public.* Same answer, and for the same reason `agency-listing` gave: the
published item is the **output**; this row holds the **file that produced it**. The published
governance statement is three pages; the board packs behind it are a year of them, including the
papers that were withdrawn, the appendices that were never quoted, and the minute of the item that
was resolved not to proceed. Publication of the output does not lower the posture of the input.

The correct direction, and the three grounds on which this row's rules genuinely differ from the
family default:

1. **Aggregation is this row's normal case, not its exception.** `00`'s corpus sentence lists what
   the product handles — it *"can include identity documents, account statements, tax records,
   medical information, legal records, credentials, private correspondence, GPS metadata, employment
   materials, and educational records"*. A single routine board pack carries a **remuneration
   appendix** (employment materials), a **finance appendix** (account statements), and a **legal
   memo or litigation update** (legal records) **behind one cover page and inside one PDF.** The
   schema anchor already names attachment carriage as a family ground; what is different here is
   *density and routineness* — for this row it is the ordinary weekly shape of the artifact, not an
   occasional attachment. No other sibling's default document is a container of three of `00`'s named
   categories at once. This is a difference in kind, and it has an operational consequence the JSON
   records: **a pack must not be treated as one document for grouping purposes**, because its papers
   are separately meaningful *and separately sensitive*.
2. **Third parties who cannot consent, in three distinct populations.** The schema anchor's leg-3
   ground is that the exposed party is usually not the user. This row sharpens it by naming *who*:
   **named employees** whose pay, performance and exit terms appear in a remuneration or nominations
   paper; **a counterparty to a transaction that has not been announced**, whose interest in
   confidentiality is commercial and time-limited and absolute until it lapses; and **a litigant or
   a complainant**, who appears in a legal or whistleblowing update by name and often at the worst
   moment of their dealings with the organisation. None of the three is operating the product. Marked
   as **inference** — `00` does not describe board material.
3. **Legally privileged advice is routine here and nearly invisible.** A board paper attaching
   counsel's advice is `00`'s *legal records* category, and the thing that makes it a distinct
   privacy problem rather than a louder version of the family's is that **the privilege attaches to
   the document and can be lost by its handling**, which is not true of ordinary commercial
   confidence. Also inference.

**The stricter posture the dispatch asked about cannot be expressed, and that is the finding.** The
catalogue's sensitivity vocabulary is exactly `none | potentially_sensitive`; there is no third value
and this row may not invent, alias, rank or infer one, because handling classes are P7's. So the row
does what it can and says plainly what it cannot:

- `sensitivity` is `potentially_sensitive` — the strictest value available — with **no P7 handling
  class assigned.**
- Every entry in `recognition.deterministic` is prefaced by a precondition that it is a **detection**
  signal and **never an extraction licence**, on *"Privacy policy must be enforced before content
  reaches any model or external connector."* A row with eight rich structural signals sitting on a
  schema with zero fields must not be read as licensing extraction, and this is the same discipline
  `agency-listing` adopted for the same reason.
- `recognition.needs_llm` carries its own precondition that any model step runs **after** P7, on
  *"Protected material should not be included in cloud-model prompts by default, should not display
  raw content in general group summaries, and should not be moved automatically without a user policy
  that explicitly permits it."*
- The only remaining lever is **routing**, and the row uses it: three of the eleven fixtures — the
  approved minutes, the written resolution, and the equity board consent added this pass — route to
  **Protected Records** when this row does not activate, rather than to the softer `Review Later`.

The residue is exactly **NJ-J-IND-4**, carried from the schema anchor: if the desired posture is
genuinely stricter than `potentially_sensitive` and `is_safety_domain` correctly stays with `00`'s
four, then some substitute mechanism must exist and it must be named by someone with authority to
name it. This row is the sharpest instance of that gap in the family and says so.

**Verdict on leg 3: passes, on aggregation density, the three named non-consenting populations, and
privilege.**

**Overall: the row stands, on legs 2 and 3, with leg 1 explicitly conceded and its specific hazard
named.** The gist draft's "stands" verdict is confirmed, not reversed — but the gist draft asserted
that "dimensions do not differ" without noticing that the family default's own example *is* this
row's shape, which is the more interesting version of the same concession.

---

## Applying the family's never-alone principle, signal by signal

The schema anchor requires every sibling to audit its detection signals against one rule: **pair a
structure with a labelled slot; never rest on an entity name, a business vocabulary word, or a
document shape alone.** This row is unusually exposed to that rule, because the refusal it sits
nearest — `organisational-records` — was refused for resting on *an organisation name plus a
document-type word*, and **"Acme Ltd" + "minutes" is precisely that pattern.** The audit, honestly:

| Signal | Structure | Labelled slot | Verdict |
|---|---|---|---|
| Convening structure | notice-period or quorum statement | named body + date/time + venue slot | **Pairs.** |
| Papers index | numbered index with decision/noting column | per-item author or sponsor slot | **Pairs.** Strongest. |
| Minute structure | attendance + numbered items + resolution block + actions table | attendance/apologies list, agreed-by line | **Pairs.** |
| Written resolution | recital + operative clause | signature and circulation block, named body in title | **Pairs.** |
| Governing instrument | matrix of decision types × approval levels × thresholds | version / owner / approver / review-date header | **Pairs.** |
| Recurring calendar entry | recurrence rule present | labelled `SUMMARY` naming a body; attendee slots | **Pairs, weakly** — and it is explicitly written as contributing only once content evidence exists, per CONNECTION-EXAMPLES fixture 5. |
| Parent-folder context | — | a body or meeting-date folder name | **Does not pair.** Written in the JSON as *"a clue that raises plausibility once one of the structures above is already present. Folder context never fires alone."* Correct as written. |

And the demotions to `never_alone`, each of which is a candidate signal this row deliberately
**refuses** to rely on:

- **An agenda, an attendance list, or a minutes heading alone.** Every organisation, club, PTA and
  project team on earth produces those. This is the row's tempting false shape.
- **Governance vocabulary alone** — board, committee, resolution, quorum, apologies, chair. A
  corporate-governance textbook chapter, a saved regulator guidance PDF and a director-induction
  training deck are *denser* in this vocabulary than a real minute is, and none is a body's own
  record. `00`: *"Topic answers what a file is about, while purpose answers what the file was for."*
- **A company or charity gazetteer hit alone.** The read-across from *"A university name alone should
  not create a group because Columbia can appear as an authoring school, course provider, target
  institution, employer, research venue, or merely a cited organization."* — marked **inference**,
  because `00` writes that sentence about a university. A company name is *worse* than a university
  name for this purpose: it appears as employer, customer, supplier, competitor, regulator, and as
  the letterhead of a document that is merely **about** the holder.
- **`source_type` or extension alone**, on *"treat the file extension as a routing signal rather than
  an assumption about meaning"* and CONNECTION §5 invariant 2.
- **A download-session membership alone**, on *"A session should never be treated as proof of
  topic"* — and this row needs that rule badly, because emptying a board portal in one go is the
  normal way this material arrives.
- **A PDF author/producer/company metadata string alone**, on *"PDF metadata should be treated as
  supporting evidence, not as truth"* — a corporate template stamps the same entity on every blank
  form it ever generated.
- **A bare 4-digit number** read as a fiscal year, an entity number, a resolution number, or a
  document version.

**So why is this row not `organisational-records`?** Because the refused row had *nothing but* the
never-alone evidence, and this row's activation never uses it. Strip the entity name and the word
"minutes" from a real board pack and the numbered papers index with its decision/noting column is
still there, the quorum statement is still there, and the operative resolved clause is still there.
Strip them from `organisational-records`' candidate evidence and nothing remains. That is the whole
difference, and it is the correct test.

---

## Files considered and rejected

A row that only lists what it holds has not been researched. The tempting false positives, and what
discriminates each.

| File | Why it is **not** this row's evidence |
|---|---|
| **`Board minutes template.docx`** — kept as the row's **primary collision fixture** | A complete minute structure — attendance, numbered items, resolution block, actions table — with every value slot empty or bracketed, and a governance institute's brand in the footer. **Every structural signal this row owns fires, and the file is not a record.** Discriminator: *"purpose answers what the file was for."* It was for showing someone how to write a minute. Routes to **Reference Clips**. |
| **`Leadership team meeting notes 2026-03-04.docx`** — the second fixture | A meeting header, attendees, bulleted discussion, an actions list with owners — and **no terms of reference, no quorum statement, no resolution.** The sibling `meeting-record` owns it, and says so from its own side. |
| A **corporate-governance textbook chapter** or a saved **regulator code of practice** | Maximally dense in this row's vocabulary; contains no body's own record. Topic, not purpose. Routes to **Reading Inbox**. |
| A **director-induction training deck** | Governance shape, governance words, and a teaching purpose. Same discriminator. |
| A **published listed-company annual report** | Considered and dropped, and the reasoning is the leg-3 one: it is the governance cycle's **output** made public. Once published it is reading material about the company, not the body's working record. |
| A **shareholders' agreement** | Dropped. It is an **instrument** between shareholders, not a body's decision record. `finance.cap-table-equity` and the legal family own it. |
| A **remuneration-committee benchmarking report** | Real, and genuinely in this row's folder — but it is a **market-research artifact wearing a governance subject**, and the family anchor is explicit that a topic word is not a node. A `work_type`-adjacent case, not an example. |
| A **`.vcf` of directors' contact details** | `00` requires contact data be privacy-protected rather than used to create folder proposals. A file-kind signal at most. |
| A **company registration certificate** with no body around it | A standalone instrument with a durable purpose and no cycle. **Independent Records.** |
| An **auditor's management letter** | Arrives *to* the audit committee and is discussed in a pack — but its structure is a finding + a corrective action + an owner + a due date, which is `compliance-audit`'s structure, not a pack index. |
| A **board dinner invitation** or a **venue booking confirmation** | Names the body, carries a date, and records nothing the body decided. **Receipts and Confirmations** or **Independent Records**. |
| A **`.zip` board-portal export**, password-protected | Kept as a fixture, but the discipline is the point: *"the normal scan should never extract archive contents to the filesystem"*, so the manifest proposes a review and propagates nothing. **Unsupported or Encrypted.** |
| A **screenshot of a board portal page** | Kept as a fixture for the negative rule. Portal chrome with a paper list and a voting control, no labelled slot, a system-generated filename. And *"the system must not mistake the absence of EXIF for proof that an image is a screenshot"*. **Temporary Screenshots.** |

---

## The collision fixture, in both directions

The addendum asks for both: a real file that would **wrongly fire** this row, and a real file that
must not be **lost to** it.

**Would wrongly fire this row: `Board minutes template.docx`.** Argued above. It is the row's
hardest case precisely because the discriminator is not in the structure at all — the structure is
*perfect* — but in the emptiness of the value slots and in the footer brand. This is why
`recognition.needs_llm` leads with "separating a real minute from a blank minute template, a sample
pack published by a governance institute, or a course case study", and why the abstention rule is
attached: *"A model that cannot cite sufficient evidence must return unknown."*

**Must not be lost to this row: `Unanimous Board Consent - Equity Grants and FMV Approval.pdf`.**
These are the **same bytes** the landed `finance.cap-table-equity` launch row names as one of its own
fixtures, with the observations *"heading identifies the board of Acme Robotics, Inc. and a unanimous
written consent"*, *"resolutions approve a common-stock fair market value, individual option grants,
and an attached grant schedule"*, *"director signature blocks are completed"*. Every structural signal
this row owns fires on it — a named body, a written resolution with no meeting, a signature block —
and **this row must not take it.** The seam is stated reciprocally in the next section. It is added
to this row's `file_examples` this pass, so that both sides name the same bytes.

---

## Reciprocal boundaries

Written from this side, after reading the neighbour's own file, and not contradicting it.

### `business_operations.meeting-record` — the load-bearing seam, and the reciprocal already exists

**A board meeting is a meeting.** The dispatch is right to insist this be stated rather than assumed:
there is no natural-language sense in which a board meeting is not a meeting, so the boundary is
entirely a construction of this catalogue and has to be justified as one.

The sibling has already written its side, and it is quoted here verbatim from its JSON so that this
row cannot drift from it: *"A board or committee produces agendas, minutes and actions in exactly
this shape, and the same file may be called minutes by both. The discriminating evidence: a notice of
meeting, a quorum statement, numbered papers, register of interests, or formal resolutions supports
governance; an unowned working meeting with no constitutional apparatus supports this row."* Its
`one_line` narrows itself explicitly and in this row's favour: it is *"a WORKING meeting that no
other situation already owns"*, and agendas and minutes produced **inside a governance cycle** belong
to the governance row, *"where they are values of work type."*

**This row's side, stated to match:** the discriminator is **constitution, not vocabulary.** Terms of
reference, a quorum, and a resolution with standing outside the room support this row. A leadership
team that writes the words "minutes" and "actions" but has no terms of reference, no quorum and no
resolution is the meeting-record row's, and the fixture `Leadership team meeting notes 2026-03-04.docx`
is carried on this row **as a negative** saying exactly that. Meeting vocabulary discriminates
neither direction.

Two things are worth stating that the gist draft did not:

- **The sibling's narrowing is doing most of the work, and it is asymmetric.** `meeting-record` is
  defined residually ("no other situation already owns"), so in a genuine tie the *sibling* yields,
  not this row. That asymmetry is the sibling's own choice, stated in its own `one_line`, and this
  row accepts it rather than claiming it — but it should be visible to R1c that the seam is not
  symmetric, because an asymmetric seam behaves differently under P10.
- **A shared-bytes case both rows should recognise:** an executive committee that has adopted terms
  of reference but passes no resolutions. Constitution present, standing absent. This row's honest
  answer is **abstain and route to Review Later**, not to claim it — and the sibling should not claim
  it on the strength of "working meeting" either. Flagged as **NJ-BO-GOV-2** below rather than
  resolved unilaterally, because the sibling is being deepened in parallel and this row may not edit
  it.

### `finance.cap-table-equity` — the equity seam, on the same named bytes

**In this direction:** a board consent that approves a share issuance, an option grant or a fair
market value **is** a written resolution of a constituted body, and every one of this row's
structural signals fires on it. **This row still does not take it.** The landed launch row's
discriminator governs, and it is a *content* discriminator, not a shape one: it requires that *"the
equity-grant and FMV resolutions are the independent evidence"* and forbids *"Finance activation from
the board heading, signatures, or company name alone"*. Where a capitalization ledger, a share or
grant structure, an issuance resolution, or a valuation structure is present, the equity content is
the specific evidence and Finance — a **safety** schema — is the correct home. Governance shape is
the generic evidence and must yield to it.

**In the other direction:** a written resolution of the same body that appoints a director, adopts
terms of reference, approves a policy or notes a management account has **no equity content at all**,
and `cap-table-equity` must not take it merely because it carries a board heading and director
signatures — which is what that row's own `never_alone` entry already forbids: *"a signature block,
board heading, governing-law clause, or e-signature envelope alone. These are generic legal-document
structures."* On this seam the two rows agree, and the agreement is load-bearing: **the board heading
is never-alone on both sides.**

**The seam is currently one-way in the catalogue.** `finance.cap-table-equity` names
`career.employment-records`, `finance.insurance-corporate` and `photos.screenshot-captures` among its
collisions; it does **not** name `business_operations.board-governance`. This row names it (added
this pass). That is an instance of the schema anchor's NJ-BO-4 — *"No landed row on the roster names
`business_operations` except `construction_property`"* — and it is recorded rather than fixed, since
this row may not edit a landed launch row.

### `business_operations.corporate-regulatory-filings` — a resolution becomes a filing

**In this direction:** a body's own signed resolution, with a circulation block and no submission
apparatus, is this row's. **In the other:** a registry form, a submission reference, a filing
deadline, or an authority's acknowledgement is the filings row's — its anchor is, in its own words,
*"an OBLIGATION TO AN AUTHORITY with a deadline and a filing reference — a document whose existence
is compelled from outside."* The resolution's existence is compelled from **inside**, by the body's
own constitution. That is the cleanest discriminator on any of this row's seams.

The two live in one folder constantly — appoint a director, minute it, file the form, keep the
receipt — and `00` settles that case rather than this row having to: *"A file may validly belong to
more than one accepted group"*, with placement decided later. This seam is also **one-way**: the
filings row lists nine collisions, including `finance.cap-table-equity` for share allotments, and
does **not** list this row. Same NJ-BO-4 residue.

### `business_operations.compliance-audit`

An audit committee's papers are simultaneously a governance cycle and an audit record. **This
direction:** a pack index, attendance and resolutions. **The other:** a finding, a corrective action
with an owner and a due date, or an auditor's report structure. Note the shared hazard with
`meeting-record`: *an actions table with owners and due dates* is common to all three rows, so it
must never be a sole signal for any of them, and it is not.

### `nonprofit.governance`, `law_practice.corporate-secretarial`, `government.public-authority-record`

Not yet landed; the edges are written from this side and are inferences.

- **`nonprofit.governance`** — a charity's trustee board, a union's executive and an association's
  council produce byte-identical notices, packs and minutes. Discriminator is **owner type**: trustee
  or member-body vocabulary plus a charity or union registration slot and a purpose-of-association
  framing on one side; a share-capital, director and commercial-counterparty framing on the other.
  Governance *shape* activates neither.
- **`law_practice.corporate-secretarial`** — a practitioner runs a client's company secretarial work
  and produces exactly these documents **for someone else's body**. Discriminator is the **matter
  anchor**: a matter identifier, an engagement or client framing, or a time-recording or billing
  anchor is the practitioner's; the same minute held by the entity it is *about*, with no matter
  anchor, is this row's. This is the schema anchor's "side" rule, and when the side is unrecoverable
  from the file the required outcome is abstention.
- **`government.public-authority-record`** — councils, agencies and school boards publish notices,
  agendas and minutes in the same shape and often publicly. Discriminator is again which side the
  holder is on: a statutory power, a public-notice obligation or a published-agenda framing on the
  authority side; a private body's own confidential pack on this side.

---

## Neighbours considered that did **not** get an edge, with the reason

The dispatch's `must_consider_neighbors` were `career`, `finance` and `hr`.

- **`career`** — **no edge, and this is the clearest of the three.** `career` is a person's *own*
  record of their working life. A non-executive director's personal folder of the boards they sit on
  is the one real case, and it does not need an edge: the *documents* are still the body's record,
  and what makes it `career` would be a CV, an appointment letter held as a personal record, or a
  fee arrangement — none of which carries this row's structures. The schema anchor's anchor-triple
  test resolves it without a collision entry.
- **`finance`** — **edge granted, to `finance.cap-table-equity` specifically** (added this pass), for
  the reason argued above: it is the one place where the same named bytes are contested. The broader
  `finance` seam is the family's NJ-J-IND-3 (where does an organisation's money live) and belongs to
  the schema anchor, not here. A board's *review* of management accounts is not a finance record; the
  accounts are, and they are `budget-forecast`'s or `finance`'s depending on that unresolved seam.
- **`hr`** — **no edge, and this is a deliberate refusal that deserves its reason.** Remuneration and
  nominations committee papers are genuinely both governance and HR material, and it is tempting to
  edge `hr.compensation-planning`. The reason not to: the material only crosses **when it names
  individuals**, and the schema anchor already states that boundary family-wide ("a single spreadsheet
  crosses into employee-identifying material at one column; where it does, the stricter side wins").
  Restating it here would add **no discriminator** — it would be the same rule in a second place,
  which CONNECTION §9 treats as duplication rather than coverage. What this row does instead is
  operational and does more good: the remuneration appendix is named in leg 3 as the aggregation
  problem, and the approved-minutes fixture routes to **Protected Records**.
- **`business_operations.risk-register`** — a board risk report. Same shape of reason: the
  discriminator is the register's likelihood/impact scoring columns, which is the risk row's
  structure and not a governance one. No edge; the risk row's own structure test settles it.
- **`business_operations.policy-handbook`** — a policy approved at a board meeting. The approval is
  minuted here; the policy is the handbook row's. No edge needed because the two documents are
  different files, not the same bytes.

---

## `proposed_fields` — none, deliberately, and the abstention is the argument

`proposed_fields` is **empty**, and this row wants two keys it is refusing to mint:

- **`fiscal_period`.** A governance calendar is annual and the cycle is its spine. But this key is
  **already proposed by the schema anchor**, with `destination_eligible: true`, `reliability_ceiling:
  "validated"`, and the rule family named (a fiscal-period token pattern co-occurring with a
  period-context term in the same labelled block — no regex written, R2/R6 own that). The anchor
  states that **four rows in this family want this key and none can have it**, naming
  `budget-forecast`, **`board-governance`**, `corporate-regulatory-filings` and `compliance-audit`.
  This row is one of the four and **seconds the existing proposal rather than minting a variant** —
  no `governance_year`, no `board_year`, no `meeting_period`. Minting any of those would be exactly
  the synonym failure the dispatch prohibits.
- **A BODY key.** This is the one genuinely new field-shaped hole this row found, and it is
  **deliberately not proposed.** The argument for it: it is what a company secretary actually files
  by, it is not an entity collector, and it would be the row's natural top dimension. Three arguments
  against minting it here: (a) the schema declares **no** fields, so a template minting a key on a
  field-less schema at its point of maximum temptation is the 574's mistake performed knowingly — the
  anchor makes exactly this argument when it declines to mint a supplier role key; (b) it is very
  close to `organization`, which the anchor has already proposed and which R1c must adjudicate **once**
  for both this family and `construction_property`, and a second entity-shaped key would muddy that
  single decision; (c) it has an unresolved **privacy** cost of its own — a folder named for the
  remuneration committee discloses in the filesystem namespace that the material exists and what it
  concerns. That cost is why it is an open question rather than a proposal. Raised as
  **NJ-BO-GOV-1**.

`proposed_context_terms` carries 29 practice terms (`notice of meeting`, `terms of reference`,
`quorum`, `IT WAS RESOLVED`, `matters reserved`, `delegated authority`, `for decision`, `for
noting`, `declaration of interest`, `proxy`, `company secretary`, …). These are **proposals**, not
`00`'s floor — `00`'s only named context-term floor is the academic one, and this row does not
pretend otherwise. Several overlap the schema anchor's 40 (`quorum`, `terms of reference`) and are
seconds, not variants.

---

## Sparse-file discipline

Five of the eleven fixtures carry `group_without_copying_facts: true`, and this world needs the rule
more than most, because **the pack is a container of sparse members by construction**. A cover note,
a blank feedback form and a slide with three words on it sit inside the same PDF as a fully
identified finance appendix. `00` covers the shape — *"The documents are content-incoherent but
purpose-coherent."* — and the prohibition — *"The graph does not automatically copy those missing
facts onto sparse files."* The `grouping_reasons` entry that names "one decision as it travels" is
flagged in the JSON as **the reason most likely to tempt a body label onto a sparse member**, which
is the correct place to put the warning.

The stop rule is quoted as written — *"when members carry irreconcilable course, institution,
project, term, or purpose facts"* — and applied: **two different bodies' minutes in one folder do not
merge.** And *"no group at all is a valid outcome"*: a stray set of terms of reference is an ordinary
standalone record and goes to **Independent Records**.

---

## NEEDS-JOSEPH

- **NJ-BO-GOV-1 · Is a constituted BODY an acceptable branch anchor in v1?** *(This was numbered
  NJ-BO-4 in the gist draft. **Renumbered this pass because the deepened schema anchor now uses
  NJ-BO-4 for a different question** — the missing reciprocal edges. The collision was real and would
  have confused R1c.)* It is the level a company secretary actually files by, and unlike a bare
  entity name it is not the vanity collector `00`'s template validator rejects. Against it: a folder
  named `Remuneration Committee` or `Audit Committee` **discloses in the filesystem namespace** that
  the material exists and what it concerns — a namespace-level disclosure that no field-level privacy
  rule can undo. Alternatives and costs: **(a)** a shallow, user-approved body level with no automatic
  internal depth — this row's provisional posture, cheap and reversible, but it still discloses;
  **(b)** no body level, function first — safe, but scatters one committee's year across four function
  folders and loses the thing the user files by; **(c)** body level with a neutral label chosen by the
  user — preserves the shape and removes the disclosure, but the mapping has to live somewhere and
  nothing in the catalogue owns it. Joseph's call. **It does not depend on whether
  `business_operations` ever gets field rows**, which is why it is stated separately from NJ-BO-1.
- **NJ-BO-GOV-2 (new) · The constituted-but-non-resolving body.** An executive committee with terms
  of reference that passes no resolutions sits exactly on the `meeting-record` seam: constitution
  present, standing absent. Alternatives: **(a)** this row takes it on the terms of reference —
  simple, but weakens "standing outside the room" to "has a document called ToR", which a great many
  working groups now have; **(b)** `meeting-record` takes it — consistent with that row's residual
  self-definition, but files a constituted body with the stand-ups; **(c)** abstain to **Review
  Later** — this row's provisional answer, honest but leaves real material unplaced. Cannot be
  settled unilaterally: `meeting-record` is being deepened in parallel and this row may not edit it.
  **R1c must land (a), (b) or (c) on both rows at once.**
- **NJ-J-IND-4 (carried, and this row is the family's sharpest instance)** — the third-party
  confidentiality gap. This row correctly does **not** carry `is_safety_domain`, and the sensitivity
  vocabulary offers nothing stricter than `potentially_sensitive`. But its ordinary artifact carries
  three of `00`'s named corpus categories at once, about three populations of people who are not the
  user and cannot consent, and sometimes under legal privilege that its handling can destroy. If the
  flag stays with `00`'s four, **the substitute mechanism must be named by someone with authority to
  name it.** Alternatives as the anchor states them: a fifth safety domain (breaks D-ratified scope);
  per-row `potentially_sensitive` that P7 already honours (current assumption — is it enough for
  privileged material?); or an explicit third-party-confidentiality flag on the sensitivity block
  (new mechanism, needs an owner).
- **NJ-BO-4 (carried, and this row supplies two fresh instances)** — the reciprocals are missing.
  Neither `finance.cap-table-equity` (a landed launch row) nor
  `business_operations.corporate-regulatory-filings` names this row, though this row names both and
  `cap-table-equity` carries the shared `Unanimous Board Consent` bytes. R1c either adds the return
  edges or the activation logic must be defined to tolerate asymmetric edges.
- **NJ-BO-1 (carried)** — `organization` and `fiscal_period` as canonical keys. This row is one of
  the four that wants `fiscal_period` and seconds it rather than proposing a variant.
- **NJ-BO-3 (carried)** — `role_split` key spelling is inconsistent across the landed catalogue. This
  row's `role_split` is `[]`, so it is not affected, and it does not normalise anything unilaterally.

---

## What changed in this pass

**Preserved, unchanged and deliberately not rewritten** (the gist draft was verified, not untrusted):

- The whole `recognition` block — all 8 `deterministic`, 7 `needs_llm` and 8 `never_alone` entries,
  with their preconditions. This pass **audited** them against the schema anchor's never-alone
  principle (the table above) and confirmed every one; it changed none.
- All 29 `proposed_context_terms`, all 17 `work_types`, all 6 `grouping_reasons`.
- `template.dimension_order: []` with its full `why` prose, `time_first: false`.
- `file_kinds` (9 source types, 12 extensions, `never_alone: true`).
- All five `falls_through_to` entries with their quotations.
- `sensitivity: potentially_sensitive` and the whole of `sensitivity_why`. The leg-3 argument above
  **extends** it with density, the three named populations and privilege; it does not reverse it.
- All six pre-existing `collides_with` entries, verbatim.
- The ten pre-existing `file_examples`.
- `fields: []`, `proposed_fields: []`, `provenance: "proposal"`, `design_cite: null`,
  `refuse_node: false`, `role_split: []`, `also_holds_with: []`.

**Added to the JSON this pass** (two structural additions, both named by the dispatch):

1. A **`collides_with` entry for `finance.cap-table-equity`**, stated in both directions and naming
   the shared bytes. The gist draft routed this seam indirectly through `corporate-regulatory-filings`
   and said so honestly; the dispatch is right that the equity seam is direct and belongs stated
   directly.
2. An **eleventh `file_example`, `Unanimous Board Consent - Equity Grants and FMV Approval.pdf`** —
   the same bytes `finance.cap-table-equity` names, carried here as a **negative** fixture, routing to
   **Protected Records** if inactive.
3. `open_question` updated to renumber the body question to **NJ-BO-GOV-1** and to add NJ-BO-GOV-2.

**Added to the memo this pass:** the three legs argued individually with a verdict each (leg 1 now
concedes, and names the specific hazard that the family default's own second level *is* this row's
shape); the signal-by-signal never-alone audit against the schema anchor's family principle, with the
explicit "so why is this row not `organisational-records`" test; a Files-considered-and-rejected table
of thirteen entries, up from five; the collision fixture in **both** directions; reciprocal boundaries
for seven neighbours, each written after reading the neighbour's own file and quoting
`meeting-record`'s side verbatim; the reasoned non-edges for `career`, `hr`, `risk-register` and
`policy-handbook`; the sparse-file discipline section; and two new NEEDS-JOSEPH items.

**Reversed:** nothing. The gist draft's "stands" verdict is confirmed on better evidence, and its one
substantive judgement — that the discriminator against `meeting-record` is **constitution, not
vocabulary** — is adopted as written, because it is right and the sibling's own file agrees with it.

**Nothing outside this row's two files was written or edited.**

---

## Audits run before returning

- `python3 -m json.tool` on the JSON — parses.
- Key set diffed against `business_operations.meeting-record.json` and
  `business_operations.corporate-regulatory-filings.json` — identical top-level key set.
- Every curly-quoted string in both files extracted programmatically and checked: **27 distinct
  strings match `planning/00-database-agent-product-design.md` verbatim**; the remaining 14 are
  quotations of neighbour catalogue files (`meeting-record`, `cap-table-equity`,
  `corporate-regulatory-filings`, the schema anchor) and each was verified verbatim against its own
  source file. Zero unmatched.
- `SOURCE_TYPES` checked against `src/evidence_shape/vocabulary.py` — all nine are members.
- `fields: []` and `proposed_fields: []` confirmed; no canonical key minted anywhere in either file.
- `sensitivity` is one of `none | potentially_sensitive`; no P7 handling class assigned.
- Files written: exactly the two assigned. `meeting-record`, `cap-table-equity`,
  `organisational-records` and `corporate-regulatory-filings` were **read only**.
