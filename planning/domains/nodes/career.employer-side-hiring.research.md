# Lab notes — `career.employer-side-hiring`

Kind: `template` · `schema_id: career` · launch `placeholder` · provenance `proposal`
Output: [`career.employer-side-hiring.json`](career.employer-side-hiring.json)

---

## Sources actually read

- `planning/00-database-agent-product-design.md` — **in full**. Every quoted span in the node was
  grep-verified against this file before it was written; a mechanical re-check of the finished
  node found **51 quoted spans, 0 not verbatim**. The one non-`00` quotation I had drafted
  (CONNECTION's PR-6 phrase) was de-quoted rather than kept, because it is line-wrapped in its own
  source and I would rather paraphrase than ship a span that fails a literal substring check.
- `planning/domains/_CONTRACT.md` — rules 5 (sensitivity is `00`'s phrase, no handling class), 8
  (snake_case; a template may only branch on a field its schema declares), 10 + 15 + PR-6 (career
  writes no field rows), 12 (one schema per template), 14 (closed edge vocabulary).
- `planning/domains/CONNECTION.md` — §2 node test, §3 no schema inheritance, §5 the closed edge
  table (this is where I learned `also_holds_with` is **schema ↔ schema only**, which changed my
  plan; see below), §6 canonical fields, §7 four objects four owners.
- `planning/domains/CONNECTION-EXAMPLES.md` — fixtures 1 and 2, for the observations/facts split
  and for what an `also_holds` file looks like at file level.
- `planning/prompts/ALIGNMENT.md` — the two roster kinds and the "a template that only repeats its
  schema's default is not a node" test.
- `planning/domains/canonical_fields.json` — read end to end. No career-shaped key exists; the
  closest candidates (`institution`, `client`, `our_firm`, `application_cycle`,
  `application_document_type`) are all scoped to other roles.
- `planning/domains/roster.json` — confirmed my id, kind, `schema_id`, neighbours, and every id I
  put on an edge (all 10 edge targets verified present on the roster programmatically).
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`; all 12 `file_examples[].source_type` values
  and all 8 `file_kinds.source_types` verified members.
- Landed neighbour nodes, read rather than rewritten: `career.json` (the placeholder schema),
  `career.recruiting.json` (my mirror image, and the row that already authored an edge at me),
  and the two other rows that already name me — `career.employment-records.json` and
  `academic.recommendation-letters-written.json`.

`planning/01-product-design-structured.md` was **not** read: nothing in the node needed a section
locator, and `00` is the authority on every claim made. Recorded so the omission is deliberate.

---

## Node test — why this is a node and not padding

The refusal bar is: a template whose detection signals, recommended dimensions **and** privacy
rules are all its schema's default is not a node. This row clears it on two of the three, and the
second one is the reason the row exists at all.

1. **Detection signals differ structurally, not by vocabulary.** The discriminator I settled on is
   an *inversion*, not a term list: `career.recruiting` is one person's documents across many
   employers; this row is many different people's documents under one requisition. That inversion
   is readable from an archive manifest, from a spreadsheet's column headers, and from an email's
   sender/recipient/subject slots, and it is not expressible by any word. Two document kinds also
   exist only here — the interview scorecard (two named-person slots, a rating scale, a labelled
   recommendation) and the candidate-pipeline export.
2. **Privacy rules differ in kind.** Every other career situation holds the user's own material.
   This one holds, as its *ordinary* content, living third parties' resumes, contact details,
   identity pages and candid evaluations of them. That flips the residual default: `Protected
   Records` is this row's primary fall-through rather than its exception, which is a privacy rule
   no other career row has.
3. Dimensions are the one axis where I could **not** claim a difference honestly, because the
   career schema declares no fields and every career row's `dimension_order` is empty by contract.
   I did not manufacture one to look distinct. What I recorded instead is a correction to the held
   prose (below), which is a template-level finding, not a dimension.

`refuse_node: false` on that basis. Had the row been only "recruiting, but from the company's
desk," it would have been a refusal.

---

## The finding I most want R1c/P10 to see

`00`'s recorded career order — company → role or recruiting cycle → document type — **does not
transfer to this side of the process**. On the employer side the company level is degenerate: one
employer, on every file. Applied here it produces precisely the branch `00` tells the interface to
warn about ("warn when a level produces only one child"; "recommend flattening when a dimension
does not materially improve retrieval"). The level that actually organizes this corpus is the
*requisition* — a role paired with a cycle under an opening identifier — which is neither of the
two things `00`'s disjunction offers. That is a vocabulary question, so it went to `open_question`
rather than into a dimension list the schema cannot support anyway.

The second half of the same finding is a refusal to design: a per-candidate folder level is the
most natural retrieval structure here and the most dangerous, because a folder named for a person
is a personnel file about a third party, and `00` disfavours person-collectors outright ("A folder
should not become a collection point for everything produced by the same person or organization").
I recommended against it and left the decision to Joseph.

---

## Files considered and rejected

- **`Employee handbook.pdf`, `Hiring policy v3.docx`** — organizational policy documents. They
  name no candidate, carry no requisition, and would activate on the holder's own employer name,
  which this row's own `never_alone` forbids. They are a different situation (internal policy /
  reference reading), and inventing a level for them here would be the empty-industry-label
  failure.
- **`Org chart Q2.pptx`, `Headcount plan FY27.xlsx`** — workforce planning. Tempting because they
  sit beside requisitions in real corpora, but their evidence is budget and structure, not any
  named applicant; a headcount sheet is a finance-shaped artifact and pulling it in would have
  widened the row into "running a company."
- **`Payroll register Mar 2026.xlsx`** — a table of many people at one employer, i.e. the exact
  structural shape my strongest signal keys on. Rejected as an example *and* used as the reason my
  spreadsheet `never_alone` entry names mailing lists, class rosters, guest lists and payroll
  registers explicitly: many-people-in-labelled-columns is not evidence of a pipeline. Its own
  home is `finance.payroll-received`.
- **`LinkedIn export.csv` / a sourcing list** — a list of people who never applied. Real, but it
  is a contacts-shaped artifact and `00` is unambiguous that such data "should normally be
  privacy-protected rather than used to create folder proposals". Including it would have invited
  a folder level over people's names.
- **`recruiter.vcf`** — already carried by `career.json` as its contacts fixture; not repeated.
- **`Take-home - data challenge.zip`** — the employer-side copy of the assessment brief. Rejected
  because `career.recruiting` already owns that fixture and its code-project collision; duplicating
  it here would have created a second, drifting account of the same file.

Twelve examples were kept, covering: a labelled form (the JD with approval slots), unlabelled prose
(the debrief notes), a structured table (the pipeline export), OCR of the same subject matter (the
board screenshot), an archive packet with a password-protected member, email, calendar, a scanned
identity document, a file that looks like mine but is a neighbour's (the agency invoice; the
candidate resume doubles as the two-sided collision fixture), and a sparse file that joins a
neighbourhood without gaining a fact (`Debrief notes.docx`, marked
`group_without_copying_facts: true` — the HW-3 shape of this situation).

---

## `proposed_fields` — deliberately empty, and why

I propose **no** fields. Three concepts here genuinely lack a canonical key: the *requisition*, the
*document type* on the career side, and — most sharply — the *subject of an evaluation* (the
candidate). Minting any of them from a leaf template row would:

- reverse S3/D1 as narrowed, which `_CONTRACT` rule 10 says must "arrive" as an explicit decision
  and not as a plan edit, and which `PR-6` says is owed *before P10*, not now;
- add a fourth spelling of the document-kind concept beside `work_type`, `record_type` and
  `application_document_type` — the 574's exact fragmentation failure, and a fork
  `career.employment-records` already recorded rather than resolved;
- create a person-shaped key whose only use would be a per-person folder level that this same node
  argues against on privacy grounds.

So the gap is recorded in `open_question` and in the `role_split` entries, where it is visible as a
missing half of a pair rather than as an invented key. Both `role_split` rows reference existing
canonical pairs only (`authored_by ↔ target_school`, `our_firm ↔ client`); neither mints anything.

---

## Neighbours considered that did **not** get an edge

- **`career.consulting-client-engagement`** — no `collides_with`. An engagement file and a hiring
  file share the `our_firm`/`client` split but never share an evidence item: a statement of work
  and a scorecard confuse nothing. It appears only as the `neighbor` on the `our_firm ↔ client`
  role split, which is a field-level pointer and not a collision.
- **`career.credentials-licenses`** — a candidate's certification copy sits in a hiring packet, but
  the discriminator is already carried by the `career.recruiting` and `identity.core-documents`
  edges; a third edge over the same evidence item would be noise.
- **`medical.*`** — pre-employment medicals and accommodation records exist in real hiring corpora
  and would be a genuine `also_holds` case. Not authored, for the reason in the next section.
- **`applications.undergraduate-packet` / `applications.graduate-professional`** — `career.recruiting`
  already collides with both over the CV/statement shape. From this side the confusion runs through
  `applications.purpose-packet` (composition of a submitted set), which is the edge I did author;
  duplicating the other two would restate one discriminator three times.
- **`finance.payroll-received`** — the payroll register is a `never_alone` counter-example here
  rather than a collision: a hiring file and a pay statement do not share an evidence item once the
  invoice/statement structure is read. `career.recruiting` already carries the offer-versus-payslip
  collision, which is the one that is real.
- **`photos.screenshot-captures`** — the ATS board capture is a screenshot by form. I handled it
  inside the `falls_through_to` scoping and the open question instead of authoring an edge, because
  the confusion is about a *residual home*, not about two templates competing for the same file.

### `also_holds_with` is empty **by contract, not by judgement**

I had drafted three (`legal`, `identity`, `medical`). CONNECTION.md §5 is explicit that
`also_holds_with` joins **schema ↔ schema only**, and this row is a template — so authoring it here
would be inventing an edge shape. The landed sibling `career.recruiting.json` reached the same
conclusion (`"also_holds_with": []`). The real co-holding is recorded where it belongs: at file
level on `Work authorization - Chen Wei.pdf` (`also_schema: "identity"`), with an explicit note in
that example that the co-activation is a schema-level join this template row does not author.
**If CONNECTION.md and the dispatch prompt disagree here, CONNECTION wins** — the prompt's edge
table lists `also_holds_with` without the schema-only restriction, and I followed CONNECTION.

Reciprocity: three of my eight collisions are reciprocals of edges already authored at me
(`career.recruiting`, `career.employment-records`, `academic.recommendation-letters-written`), and
I adopted those rows' own discriminators verbatim in substance rather than inventing competing
ones. The other five are new and one-way pending R1c.

---

## NEEDS-JOSEPH (this node only)

1. **The requisition has no home in the vocabulary.** `00`'s career order offers "company" and
   "role or recruiting cycle"; the employer side's real organizing unit is a role-plus-cycle under
   an opening identifier, and the company level above it is degenerate (one employer, every file).
   Key, value, or group-label-that-never-becomes-a-field? Decides the default shape of a real
   hiring corpus.
2. **May a per-candidate folder level exist?** Best retrieval, worst privacy: a person-named folder
   is a personnel file about a third party. This node recommends against and does not decide.
3. **The evaluation role split is missing a half.** Every characteristic document here names a
   writer and a subject who are different people. `authored_by` exists; the subject-of-an-evaluation
   role has no canonical key, and this row minted none. Whether it should exist is a shared-
   vocabulary decision, not a template's.
4. **A residual gap.** A capture of an applicant-tracking board is a screenshot by form and a roster
   of other people's names by content. `00`'s nine names offer `Temporary Screenshots` for the
   first reading and `Protected Records` for the second, and nothing for both. This row routes such
   captures to `Protected Records` and scopes its `Temporary Screenshots` edge to captures with no
   readable third-party content. Whether R3's residual library needs a protected-capture home is
   Joseph's and R3's, not this row's to invent.
5. **Inherited, not owned by this node but blocking it:** which canonical field keys the career
   schema gets when S3/D1's deferral lifts (already on `career.json` and `career.recruiting.json`).
   Until then `dimension_order` here is empty rather than aspirational.
