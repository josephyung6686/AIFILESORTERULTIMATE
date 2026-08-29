# Research memo — `creative.publishing-title`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/creative.publishing-title.json`
Roster row: template on the field-less `creative` schema, `parent_id: null`, `launch: placeholder`
Absorbed legacy id: `pub.title-production` (ROSTER.md §Appendix A line 789)

## Result

**Accepted, on the first limb of the node test, with the second limb conceded and the third argued
as a partial claim.** The row survives because one structure in its material exists nowhere else in
the tree: a **machine-readable product record addressed to a third-party supply chain**, coupled to
a **multi-title schedule** and a **print manufacturing specification**. That is not a stage, not a
work type, not a medium and not a holder role. It is a different kind of object.

The row nearly died, and the argument for killing it is recorded below in full because it is the
most useful thing in this memo.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (full).
- Stamped assignment from `make_prompt.py creative.publishing-title` (full).
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, read for
  depth calibration only. Nothing from Legal was imported.
- `planning/domains/nodes/creative.json` — the schema anchor. Read the default template, recognition,
  work_types, grouping_reasons, file_kinds, sensitivity_why, edges and open_question. This is what
  the node test measures against.
- `planning/domains/nodes/creative.book-manuscript.json` — the one landed row that already argued a
  reciprocal boundary against this id, found by `grep -rl "publishing-title" planning/domains/nodes/`
  (single hit).
- `planning/00-database-agent-product-design.md` — grepped, not streamed. Every quotation in the JSON
  was verified verbatim against lines 31, 35, 48, 95, 114, 120 and 177 before it was written.
- `planning/domains/roster.json` — confirmed the id, its `kind`, `schema_id`, the 41 `creative.*`
  siblings and the top-level schema ids used on edges.

## THE CHARGE — the strongest case that this row should not exist

Six attacks, ordered from most to least dangerous. Four land partially and are answered; two are
fatal to particular framings of the row and forced it to be narrowed.

**1. It is a lifecycle stage, and stages are values.** The `one_line_hint` literally spells a
progression: "manuscript to typeset pages to printed edition." The creative schema's own candidate
key set includes `stage`. A row whose definition is a sequence of stages of a work that another row
already owns is a value of `stage` on that row, not a node. *This attack is correct about the hint
and wrong about the material.* The row's evidence is not the sequence. It is a set of artefacts that
have no position in any sequence at all — a season schedule spanning many works, a rights grid
spanning many territories, a title P&L that models a decision rather than records a state. None of
those is a stage of anything. The row was narrowed in response: the JSON's `one_line` no longer
leads with the progression, and the progression is demoted to what it actually is, a description of
how one text acquires three identity systems.

**2. It is a duplicate of `creative.book-manuscript` distinguished only by holder role, and an
organisation name is never-alone evidence.** This is the sharpest attack and it comes with the
neighbour's own admission attached. `creative.book-manuscript` names the shared fixture
`Nightwork - 1st pass pages.pdf` and says the bytes are identical on both sides. Its NJ-BM-4 then
concedes that the seam "turns on whether OTHER TITLES are present, which is a corpus-level
observation rather than a file-level one, and the activation algorithm reasons about files."
If the discriminator is inadmissible, the row is a role label, and a publisher's name on a copyright
page is exactly the never-alone case. *Answered, but only partly.* The answer is that the seam does
not have to rest on the corpus shape. Three artefact types exist that **an author never generates**,
and each is a single file: a title P&L, a printer purchase order, and a distribution metadata record.
An author holds proofs, a jacket and a contract; an author does not hold a document modelling unit
manufacturing cost against royalty rate across run lengths. That is a per-file discriminator and it
is weaker than the corpus one but it is local. The residue is real and is carried as **NJ-PT-1**,
deliberately unresolved so that R1c settles both rows in one decision rather than letting this row
silently contradict an authored reciprocal.

**3. It is a duplicate of `creative.print-production`.** A print spec, a proof round, a printer
quotation and a files-to-printer package are print-production's entire subject. *Answered, and the
row gave ground.* The JSON now states the concession explicitly: where a book is printed with no
product record and no list, **print-production is the correct reading and this row abstains.** The
row does not own printing. It owns the case where printing is manufacturing one member of a titled,
identifier-bearing, scheduled list whose text arrived as a manuscript. The collision fixture below
is the test of that concession.

**4. It is a medium or a length — "a book."** A book is an object with pages and a spine; objects
are not filing worlds. *Answered.* The row does not activate on book-shaped evidence at all. A
book-shaped PDF with front matter is explicitly in `never_alone` and routes to Reading Inbox,
because front matter describes a book that **exists**, not one being **made**. Every fixture that
activates the row is a production artefact, and none of them is a book.

**5. It is a duplicate of the schema's default template.** The creative schema's anchor describes
"a PROJECT at a STAGE producing an ARTIFACT, sometimes for a CLIENT," and a title in production maps
onto that with no remainder. *This attack lands on the second limb and it is conceded.* The row's
`dimension_order` is empty by contract and its prose recommendation is the schema default
**unchanged**, minus the `client` level. It claims no dimension difference. It survives on limb one
alone plus a partial limb three, and the JSON says so rather than manufacturing a dimension.

**6. It is defined by an absence — "no author drafts present, therefore publisher-side."** *This
attack is fatal to that framing and the row accepts it.* "The absence of an author's working files"
is written into `never_alone` as a prohibition against the row itself. A corpus can lack drafts
because they were deleted, because the author works elsewhere, or because one delivered file is all
there ever was. The row must activate on something present.

**Verdict: accept.** The defeating evidence is the distribution metadata record. Every other creative
sibling produces deliverables; only this one produces a **product**, and a product record is a
structured document addressed to parties outside the making relationship entirely — retailers,
wholesalers, libraries. That structure is absent from the schema default, absent from
`creative.book-manuscript`, and absent from `creative.print-production`, whose output goes to a
printer and stops there.

## The node test, three legs

**Leg 1 — detection signals differ from the schema default. PASSED, and this is what carries the row.**
The schema default's signals are LINKED-ASSET, LAYER/ARTBOARD, REVISION-ROUND, BRIEF,
DELIVERY/HANDOFF, PRODUCTION-PAPERWORK, SCRIPT and TIMELINE-AND-MEDIA. Four of this row's nine
signals have no counterpart in that list: DISTRIBUTION-METADATA RECORD, MULTI-TITLE SCHEDULE,
TITLE-LEVEL FINANCIAL MODEL and PERMISSIONS/CLEARANCE LOG. Two more are the default's shapes with a
material change — PRINT SPECIFICATION **coupled to** a jacket by a computed spine dependency (the
default's DELIVERY signal has no manufacturing coupling), and PASS-PAGES SEQUENCE as a production
round rather than an author's revision family. The remaining three are inherited honestly and are
labelled as such.

**Leg 2 — dimensions differ. CONCEDED, NOT CLAIMED.** The schema declares no fields, so no template
on it can differ on dimensions; the leg is unavailable to all 41 siblings equally. The prose
recommendation is the default order with the `client` level omitted, and the omission is not a
difference in taste — it is an **inversion of the counterparty relation** (NJ-PT-3). In publishing
the maker is the organisation and the author is the supplier, so filling `client` would put an
individual's name at a folder level, which is the authorship-as-destination case 00 forbids. One
prohibition is recorded for the pass that may declare fields: no per-proof-round folder level,
because 00 already collects "duplicate and version-family signals" universally without a branch.

**Leg 3 — privacy rules differ. PARTIALLY PASSED, marked inference.** The schema's four sensitivity
reasons are unpublished work, third-party identity in sidecar paperwork, source material, and client
confidence. This row's claim is a fifth that is a difference in *kind*: **the confidentiality is
scheduled and the schedule is printed inside the file.** An uncorrected proof states its own
embargo. Every other creative row's secrecy is open-ended. The concrete handling consequence is a
trap rather than a slogan — a past on-sale date inside a file must **not** be read as an expiry,
because a proof is not the published text. Two supporting reasons are weaker and are marked as such:
third-party financial terms in author agreements and royalty statements (which is why those two
fixtures fall through to Protected Records specifically, not Review Later), and the pseudonym case,
where the sensitive content is the *link* between two names and a filesystem discloses it by
co-location with no content ever being read. This is an inference from the material, not a design
quote, and the JSON says so.

## Files considered and REJECTED

Naming what the row does not hold was more decisive than naming what it does.

- **`Nightwork - Draft 7.docx`** — an author's numbered draft run with tracked changes. Rejected
  outright and written into the JSON as a fixture the row must not claim. It is
  `creative.book-manuscript`'s, and a delivered manuscript inside a production set does not
  retroactively claim every draft that preceded it.
- **A query letter, a synopsis, an agency submissions tracker.** Rejected. They are outward-addressed
  by an author; this row is inward-addressed into production. `creative.submission-query` owns them,
  and the neighbour already stated the reciprocal.
- **`9780000000001.pdf`** — an identifier-shaped stem on a book-shaped PDF. Rejected as a bare
  number, which 00 forbids as sole proof. Reading Inbox.
- **A purchased ebook, a public-domain scan, a self-published volume.** Rejected. Front matter,
  a copyright page and an imprint name describe a book that exists.
- **An imprint or publisher name anywhere.** Rejected as never-alone. It appears in every book any
  reader has ever downloaded.
- **A designed catalogue or an AI sheet held by a bookseller, reviewer or librarian.** Rejected as an
  activation source. These circulate outside publishing houses by design; holding one proves nothing
  about the holder's role. Kept as a fixture only for what it must *not* conclude.
- **A translator's segmented working files and glossary.** Rejected. `creative.translation-project`
  owns the translator-side engagement; this row owns the licensor-side register that led to it.
- **A retail listing screenshot.** Rejected as evidence of a production set. It activates `photos`
  on positive screen-origin evidence and OCR may read a price; neither establishes a publisher role.
- **A live publishing management system, an ONIX feed endpoint, a metadata portal account.** Rejected
  as out of scope entirely. A bounded export with a readable manifest is represented; connector
  ingestion is a later decision.
- **A per-imprint, per-format or per-territory row.** Rejected as taxonomy. Imprints are organisation
  names, formats are `SOURCE_TYPES` plus extensions, territories are values. Proposing any of them as
  siblings would be the 574 mistake.

## The collision fixture

**`Poster - Riverside Festival - print ready.pdf`**, sitting beside a printer quotation and a proof
round. It carries a print-intent PDF with bleed marks, a manufacturing specification, an ordinal
proof round and a printer letterhead — four of this row's own signals — and it is **not** this row's
evidence. What discriminates it: **no title, no product identifier, no schedule with other works,
and no manuscript upstream.** Its unit is a JOB, and a job number is not a product identifier. It is
`creative.print-production`'s, and this row abstains: "Correct abstention is a successful outcome
because the product’s goal is reliable organization, not maximum file movement."

A second collision fixture is carried for the seam that matters more: `Nightwork - 1st pass pages.pdf`,
whose bytes are identical on both sides of the author/publisher line and which neither row may claim
from the proof pages alone.

## Reciprocal boundaries

Six `collides_with` edges, each stated in **both** directions and each naming the same fixture on
both sides.

| Neighbour | Same fixture | This row claims it when | Neighbour claims it when |
|---|---|---|---|
| `creative.book-manuscript` | `Nightwork - 1st pass pages.pdf` | production apparatus surrounds it — schedule, spec, P&L, product record | it sits beside that work's own draft version family and nothing else |
| `creative.print-production` | `Nightwork - Print Spec and Quote - Ravenscroft Press.pdf` | the job manufactures a member of a titled, scheduled list | the unit is the job and no product record exists |
| `creative.periodical-issue` | a season schedule / a publication calendar | the schedule's **rows are works** | the schedule's **rows are dated issues** of one publication |
| `creative.submission-query` | a full delivered manuscript file | it arrived inward via a transmittal into production | it is a member of an outward-addressed packet with a query letter |
| `creative.translation-project` | a foreign-language edition, a rights-grid cell | the licensor-side register — grid, licence, advance | the translator-side engagement — source/target pair, glossary, counterparty |
| `career` | a jacket or a finished title PDF | production apparatus surrounds it | it is a curated finished export ordered for showing |

Four `also_holds_with` edges, all on **disjoint** evidence: `legal` (contracts and licences as
operative instruments), `finance` (P&L, royalty statement, printer PO as financial documents),
`business_operations` (a season launch as a marketing programme with an approval chain), and
`creative.print-production`, which appears on both lists because both edges are true of different
files — the jacket file genuinely is a print job **and** a title's production.

## Neighbours considered that did NOT get an edge

- **`photos`** — the schema carries the collision for capture metadata on professional camera
  originals. This row has none; a jacket photograph is `creative.commissioned-shoot`'s problem, not
  this row's. Only the screenshot fixture touches photos, and that is coactivation on the fixture,
  not a row-level edge.
- **`code`** — a metadata feed is XML, and XML is `code_structured`. That is a `SOURCE_TYPES` fact,
  not a repository. No manifest, no lockfile, no source layout. No edge.
- **`retail_hospitality`** — a product with an identifier and a price *sounds* like a product
  catalogue. Rejected as a same-evidence mutex because retail's material is inventory and point of
  sale; this row's product record is generated by the **originator** of the product and exists
  before any stock does. If R1c finds a real retail catalogue row with the same evidence, the edge
  can be added without changing anything else here.
- **`creative.creative-brief`, `creative.revision-round`, `creative.deliverable-handoff`** — these
  are cross-cutting siblings whose shapes recur inside this row. Adding mutex edges to all three
  would make every one of the 41 templates collide with them and would say nothing. The round-word
  ambiguity is instead carried in `needs_llm` and `never_alone`, where it is actionable.
- **`creative.licensing-rights`** — genuinely adjacent, and the schema's open_question already
  records the rights-and-licence field hole for R1c. No edge added here rather than duplicating a
  schema-level open question at row level.
- **`academic` / `research.manuscript-publication`** — the neighbour already handled the 'manuscript'
  word collision and academic publishing is a different supply chain. No edge.

## Fields and `proposed_fields`

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`. All four are
deliberate and none is a shrug.

One genuine field-shaped hole exists and **no key is minted for it** (NJ-PT-2): a published title
carries a permanent product identifier that is neither a title nor a project name, that resolves
assets to works, and that is the join key of every distribution record in this world. No canonical
key holds it — `record_type` is finance's, `purpose` is fenced to College applications,
`artifact_type` names the document rather than the product. `creative.book-manuscript` declined the
identical temptation for a book's own identifier and this row follows it. Minting on a field-less
schema at the point of maximum temptation is precisely the recorded failure mode.

`work_types` reuses nine values already declared by the schema and invents none, which is the correct
result: this row's difference is in its *signals*, not in its vocabulary.

## Recommendations to R1c (this row changed nothing outside its own two files)

1. Settle NJ-PT-1 and the neighbour's NJ-BM-4 **together**. They are one question asked from two
   sides. If corpus-shape observations are inadmissible at activation, both rows need the per-file
   fallback written in simultaneously.
2. If `creative.book-manuscript` is re-opened, its NJ-BM-4 sentence about "other titles" should be
   read against this row's per-file fallback list (title P&L, printer purchase order, distribution
   metadata record) rather than left as a corpus-only test.
3. If NJ-R1a-1 option (b) lands and `client` becomes a folder level, this row needs an explicit
   exemption, not a default.

## NEEDS-JOSEPH

1. **NJ-PT-1 — the corpus-shape problem.** May a corpus-level observation ("other titles are
   present") inform a file-level activation? (a) change the activation algorithm; (b) redraw the
   seam per-file on artefacts an author never generates — this row's recommendation, not taken
   unilaterally; (c) merge with `creative.book-manuscript` and distinguish by a role facet, which is
   impossible while the schema declares no field to hold a role.
2. **NJ-PT-2 — the product identifier.** (a) leave unrepresented; (b) searchable observation with no
   field — recommended and assumed; (c) mint one identifier key shared with the schema's existing
   rights-and-licence hole, since a usage grant and a product identity are both product-level facts.
3. **NJ-PT-3 — the counterparty inversion.** The maker is the organisation and the author is the
   supplier. Omit `client` for this row (this row's position), or represent the inversion, which
   would need a `role_split` this row cannot author on a field-less schema.
4. **NJ-PT-4 — self-published titles.** The seam dissolves in what is now the commonest case: one
   person holds the drafts *and* the product record. (a) both rows coactivate — taken as the working
   assumption, honest but unrecorded without a field; (b) this row wins whenever a distribution
   record exists, which would swallow the draft history; (c) neither wins and it all goes to Review
   Later, which is safe and useless. Untested against a real filesystem.

## Self-verification

- `python3 -m json.tool` parses the node JSON.
- Key set and key order match `creative.json` exactly, including `proposed_context_terms`.
- Every quotation was grep-verified verbatim against `00` before being written (lines 31, 35, 48,
  95, 114, 120, 177). No quotation is attributed to `00` that was not matched.
- Every `file_examples.source_type` is in `SOURCE_TYPES`.
- Every edge target exists on `roster.json`: `creative.book-manuscript`, `creative.print-production`,
  `creative.periodical-issue`, `creative.submission-query`, `creative.translation-project`, `career`,
  `legal`, `finance`, `business_operations`. Every `falls_through_to` name is one of 00's nine.
- `fields: []` and `proposed_fields: []`; no canonical key is minted or referenced as a fact.
- No threshold number, no confidence score, no handling class, no `public_low`.
- Two files written, both mine. No roster, canonical-fields, `check.py`, `src/`, SPEC or neighbour
  file was touched.
