# Research memo — `law_practice.evidence-exhibits`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.evidence-exhibits.json`
Roster row: template on the fieldless `law_practice` placeholder schema, `parent_id: null`, `launch: placeholder`

## Result

**Accepted, narrowly, and the charge against it is conceded in most of its parts.** The row survives on one
structural claim: an exhibit is a **re-identification layer** — a designator written *on top of* a document
that belongs to some other world, plus a **schedule that closes over the designator namespace**. That is a
different activation path from the schema's default, not a narrower filter on it. Everything else the id
suggests — "evidence", "exhibits" as document types, the lifecycle position between disclosure and hearing —
is given away in the JSON.

Two things this row gives away that a padded version would have kept: the hearing bundle (to
`law_practice.trial-preparation`) and the production stamp (to `law_practice.discovery`). It also names its
own merge direction if R1c disagrees.

## The charge, stated at its strongest before anything was written

The case that this row **should not exist** is unusually strong here, and four of its five legs land.

1. **It is a `work_type` value.** Fatal if true, and it is nearly true. The schema anchor
   `law_practice.json` already lists `"evidence, exhibit and bundle index"` in its own `work_types[]`
   array. The anchor's own words for this failure mode: *"a template row justified only by holding a
   different legal document kind is the schema's default template with a narrower filename filter."* A row
   whose whole content is "the exhibit ones" is that row.
2. **It is a document-type word.** "Exhibit" is a document-type word, and the anchor strikes
   `A DOCUMENT-TYPE WORD, AND A DOCUMENT-TYPE WORD BESIDE A FIRM OR CLIENT NAME` as never-alone. Worse, it
   strikes `EXHIBIT LABEL` by name in the same list as a bare docket or matter number. The row's most
   obvious detection signal is explicitly forbidden by its own schema.
3. **It is a lifecycle stage.** Evidence gets marshalled after disclosure and before the hearing. A stage
   is not a node; it is a position in time, and the roster already has rows on both sides of it.
4. **It is a duplicate of neighbours.** `law_practice.discovery` produces the documents.
   `law_practice.trial-preparation`'s own roster hint is *"bundles, chronologies, outlines and running
   orders"* — bundles are exhibits compiled. `law_practice.depositions-testimony` holds deposition
   exhibits. `law_practice.expert-materials` holds the material behind a report. Between them they cover
   most of what a naive version of this row would claim.
5. **It is a medium or a format.** This one does *not* land, and its failure is the first hint that
   something real is here: exhibits span every source type in the vocabulary at once, which is why file
   kind can never be the discriminator, and why the row's members are mostly *other schemas' bytes*.

### The defence, and it is narrow

Leg 5's failure is the opening. What is actually distinctive is not the exhibit but the **marking**:

- An exhibit is a **foreign document with something written on it by somebody who did not author it** —
  a designator in a consistent page position, over a host whose own structure (clause numbering, an
  account header, EXIF-bearing raster, a message thread) survives intact underneath. The evidence is the
  *layering relation*, not the token.
- The layer is meaningless unless something **closes over the namespace**: a schedule of exhibits, an
  exhibit note ("this is the exhibit marked … referred to in the witness statement of …"), or a
  production-to-exhibit crosswalk. That second artefact is a page **about another document**, with no
  subject matter of its own — a shape nothing else on the roster produces.

That pairing is what the row detects on, and it is the answer to charges 1 and 2: the *word* exhibit is
struck; the *two-leg pairing* is not a word. Charge 3 is answered by observing that marking is not a stage
but a **naming system** that recurs at witness statements, depositions, hearings and adjudications, and
persists after all of them — a schedule outlives the hearing the bundle was built for. Charge 4 is answered
in the reciprocal boundaries below, and only partly: the seam with `trial-preparation` is genuinely fine and
NJ-EX-2 names the merge direction rather than pretending otherwise.

## The node test, all three legs

The schema's **default template** is stated in `law_practice.json` and I quote its shape rather than
paraphrasing it: the precondition is *(i)* an exact matter, file or engagement reference repeated across two
or more artefacts, **and** *(ii)* at least one artefact whose labelled slots separate a practitioner or firm
role from a client role. Its dimension recommendation, held as prose, is client (only where the corpus spans
several and the user approved it) → matter → document function → period. Its sensitivity is
`potentially_sensitive`, argued on the protection of one named third party.

**Leg 1 — detection signals differ. Yes, and this is the decisive leg.** The default's precondition
characteristically **does not hold on this row's files**. `Exhibit P-14 - site photograph 2026-03-04.jpg` has
no matter reference, no client, no practitioner block and no legal vocabulary — it is a picture of a wall
with a sticker on it. `Schedule of exhibits - Hartley v Nash - trial.xlsx` has no role pair either. If this
row inherited the schema's default signals unchanged, **the schema would not fire on its most characteristic
files at all**, which is the opposite of a duplicate. The row supplies a different two-leg test
(designator + closing artefact) that reaches those files, while inheriting every never-alone strike.

**Leg 2 — recommended dimensions differ. No, and I decline to claim otherwise.** `dimension_order: []`,
as the schema requires under PR-6. The row records a fourth reason for emptiness beyond the schema's three,
and it is genuinely its own: the only sub-axis this world offers is the **designator sequence**, which is an
identifier, not a fact — branching on it produces one leaf per item, and a branch named
`Exhibit D - Patel medical records` writes a stranger's identity and condition into a path. The prose
recommendation differs from the schema's in one respect: beneath whatever matter structure the schema
recommends, the exhibit set should stay **flat**, because each host document belongs to a domain that would
want its own function level, and this row must not compete for it. That is a difference in recommendation,
but it is a difference in prose, and I do not count it as a passed leg.

**Leg 3 — privacy rules differ. Yes, along a different axis from the schema's.** The schema's claim is that
one named third party is exposed. This row's is **compilation**: an exhibit set is where a practice's corpus
concentrates other people's records from every protected world simultaneously. 00's corpus sentence reads as
a description of a heavy exhibit schedule — a collection *"can include identity documents, account
statements, tax records, medical information, legal records, credentials, private correspondence, GPS
metadata, employment materials, and educational records"* — and here all of them may sit under one letter
series, about people who are not the holder, not the client, and often not parties. Three consequences the
row states: the designator does not strip the host of its own protection; the schedule is bulk-sensitive as
a whole because its description column abstracts every sensitive document in the case onto one screen; and
public availability of a docket exhibit clears nothing about the local copy.

**Verdict: two of three legs pass on their own reasoning. Accept, narrowly.**

## Files considered and rejected

A row that only lists what it holds has not been researched. These are the tempting false positives.

- **`MSA - Exhibit A - Statement of Work.pdf` — the headline vocabulary collision.** Transactional drafting
  numbers annexes *Exhibit A, Exhibit B*. Identical word, opposite structure. **The discriminator is the
  direction of reference:** an annex is referred to *by its host instrument's own clauses* and is bound
  *into* it; an exhibit is a foreign document with a designator written *on* it, referred to by a schedule
  *outside* it. This single file is why `THE WORDS EXHIBIT, ANNEX, APPENDIX, SCHEDULE or ATTACHMENT IN A
  FILENAME` is struck never-alone. Residual: Review Later.
- **`PROD0004512-PROD0004519.pdf` — the production stamp.** A control-number stamp proves *bulk
  processing*, not tender. Discovery stamps everything; only a small subset is ever marked. Given away to
  `law_practice.discovery`. It is the reason `A BATES-SHAPED OR ZERO-PADDED CONTROL-NUMBER STAMP ALONE` is
  struck.
- **`Bundle index - Hartley v Nash - vol 2.pdf` — the hearing bundle.** Continuous pagination across a
  volume, tab letters that are *not* the exhibit series, an index running over pleadings and authorities as
  well as evidence. Given away to `law_practice.trial-preparation`.
- **`Trial exhibits - Example Holdings v Example Agency (docket download).pdf` — the over-firing risk that
  worried me most.** An internally complete exhibit set *with its own schedule* satisfies **both** of this
  row's legs and still belongs to nobody. The missing precondition is the schema's, not this row's: no
  matter, no role pair, no representation. It falls to Reading Inbox. Any future version of this row that
  drops the schema precondition will hoover up every published sample bundle in the corpus.
- **`Appendix 3 - materials considered - Dr Patel.pdf`** — an enumerated attachment set scoped to one
  report. Given to `law_practice.expert-materials`; the instructing block and opinion structure are theirs.
- **`Exhibit 12 - Lee depo - text messages.pdf`** — where the only closing artefact is one transcript's own
  exhibit index, the anchor is the **examination**, and `law_practice.depositions-testimony` is the more
  specific home. This row takes it only when a schedule spans several examinations.
- **`Exhibit set - sealed - passworded.zip`** — a designator-shaped filename and a sealing word on an
  opaque archive. Nothing is opened, nothing is concluded. Unsupported or Encrypted.
- **`Scanned exhibits - box 3 - unindexed.pdf`** — leg (ii) is missing and OCR'd designators are `possible`
  evidence at best. Review Later, not a forced classification.
- **Chain-of-custody and imaging logs** were kept as a `work_type` value rather than argued as a signal:
  in a corpus they are usually one page, and a hash-and-seizure log with no designator is
  `law_practice.investigation`'s.
- **A review platform or evidence database** is a source system, not a file node. Only a bounded export
  with a readable manifest is represented.

## Reciprocal boundaries

Each names the same fixture on both sides. All seven are one-way from here; NJ-EX-4 records the debt.

| Neighbour | Theirs when | Mine when | Shared fixture |
|---|---|---|---|
| `law_practice.discovery` | control-number stamp in a bounded production range, load file, coding log, privilege log | designator **plus** schedule / exhibit note / crosswalk closing the namespace | `PROD0004512-PROD0004519.pdf` — **I give it away** |
| `law_practice.trial-preparation` | continuous pagination across a volume, tab markers, running order, chronology, skeleton | a designator namespace and the schedule that outlives the hearing | `Bundle index - Hartley v Nash - vol 2.pdf` — **I give it away** |
| `law_practice.depositions-testimony` | notice, transcript, reporter's certificate, errata, exhibit index internal to one examination | a schedule spanning several examinations, or joining a depo series to a trial series | `Exhibit 12 - Lee depo - text messages.pdf` — **I give it away in the single-examination case** |
| `law_practice.expert-materials` | instructing block, qualifications, opinion structure, materials-considered list scoped to one report | designators applied across documents the expert did not produce, closed outside the report | `Appendix 3 - materials considered - Dr Patel.pdf` — **I give it away** |
| `legal` (safety schema) | bound party pair + execution block, or tribunal caption — its protection runs first | the cover sheet, the designator layer, the schedule | `Exhibit JB1 - supply agreement - marked.pdf` — **shared; I hold only the layer** |
| `photos.scanned-documents` | positive scan-origin evidence — scanner metadata, page-image characteristics, separator sheets | a legible designator series **closed by a schedule** | `Scanned exhibits - box 3 - unindexed.pdf` — **I give it away** |
| `construction_property.variation-claim` *(asked for this reciprocal first)* | a party's own claim file compiled by the party | a matter reference, a paginated exhibit convention, a solicitor's framing | `Adjudication bundle - Oakfield - vol 2.zip` — **I give it away**, matching their words |

The construction row's JSON already states this seam and names that fixture; my side is written to match it
rather than to compete, and adds only the designator test (an appendix series compiled by the party itself
is not an exhibit namespace).

## The collision fixture

Two, because the row has two distinct ways of firing falsely, and they fail on different legs.

1. **`MSA - Exhibit A - Statement of Work.pdf`** — the *word* collision. Discriminated by direction of
   reference (bound into a host vs. stamped onto a foreign document).
2. **`PROD0004512-PROD0004519.pdf`** — the *stamp* collision, and the more dangerous of the two because it
   is structural rather than lexical: a consistent-position identifier over foreign content is exactly this
   row's leg (i). Discriminated only by leg (ii) — nothing closes over a control range except a load file,
   which is discovery's artefact, not a schedule.

## Neighbours considered that did not get an edge

- **`law_practice.court-filing-record`** — a filed exhibit carries a filing stamp *and* a designator. Not a
  mutex: they co-hold on disjoint evidence (the receipt and the docket entry are theirs; the designator
  layer is mine). Recorded here rather than as a false collision.
- **`law_practice.pleadings`, `.orders-and-judgments`** — exhibits attach to both, but the concession to
  `legal` already covers the executed-instrument and caption evidence, and duplicating it per-row would
  turn the edge list into a practice-area taxonomy.
- **`legal.personal-legal-matters`** — the holder's own marked documents. The schema's own under-firing
  fixture (`Ellis and Co - Client Care Letter - my divorce.pdf`) already states this seam from the schema
  level; restating it here would add nothing.
- **`finance` / `medical` / `photos` as schemas** — these are *hosts*, not competitors: the exhibit does
  not displace them. Recorded as `also_schema` on fixtures, per the idiom of the landed
  `legal.practice-matter-file` row.
- **`research.reading-library`** — a published sample bundle is Reading Inbox's, and that is a residual
  decision rather than a mutex.

## `also_holds_with`, `role_split`, `proposed_fields` — all empty, and why

- **`also_holds_with: []`.** A fieldless template cannot author schema-level co-activation, and the schema
  already authored `legal`, `finance` and `identity`. The fixtures record `also_schema` instead. This
  follows the landed `legal.practice-matter-file` row, which left the array empty for the same reason.
  **Recommendation to R1c (not mine to write):** the schema's `also_holds_with` should gain **`medical`**
  and **`photos`**, because this row's evidence — a marked clinical record, a stamped photograph — is where
  those co-activations actually arise, and no other `law_practice` row generates them as routinely.
- **`role_split: []`.** The split this row would want is **producing party vs. tendering party**, and
  neither has a key. `client` / `our_firm` do not fit: the producing party of an exhibit is frequently the
  *adverse* side, which is neither. Recorded as an observation for R1c rather than as a mint.
- **`proposed_fields: []`, and the emptiness is an argument.** The obvious candidate is an exhibit
  designator (`exhibit_number`, `designator`, `exhibit_label`). **It must not be minted.** It is an
  identifier, and the schema already strikes exhibit labels as never-alone; identifiers supply *linkage
  after* a role is established, never a folder level, and a designator branch is the one-child-per-leaf
  failure plus a disclosure. The row needs it as a **group anchor**, which P9 handles without a field. The
  schema's six existing proposals (`client`, `our_firm`, `project`, `work_type`, `subject_of_record`,
  `fiscal_period`) cover everything else this row would want; `subject_of_record` is the one it needs most,
  for the same reason the schema gives — the person an exhibit is *about* is routinely neither the holder
  nor the client.

## Quotations used, all grep-verified verbatim against `planning/00-database-agent-product-design.md`

`"The documents are content-incoherent but purpose-coherent."` · `"the normal scan should never extract
archive contents to the filesystem"` · `"Correct abstention is a successful outcome because the product’s
goal is reliable organization, not maximum file movement."` · `"A session should never be treated as proof
of topic"` · `"A file may validly belong to more than one accepted group"` · `"It should not form a
supported group when there is no valid anchor"` · `"The default posture must therefore be local-first and
data-minimizing."` · `"For document and record domains, project, function, or subject usually comes before
time because putting year first scatters related work across calendar folders."` · `"A model that cannot
cite sufficient evidence must return unknown."` · `"Finance, identity, medical, and legal material should be
implemented first as safety domains, meaning the system detects and protects them before any cloud or
automated placement decision is allowed."` · `"Protected Records may represent sensitive isolated material
such as passport scans, medical documents, account statements, visas, legal forms, or credentials"` ·
`"Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected
records even when they do not meet a normal group-size threshold."` · `"Review Later may hold files whose
meaning is partly understood but whose final location requires a future decision."`

No pattern catalogue, gazetteer, regex, threshold or handling class appears anywhere in the node. Designator
*shapes* (a letter series, a party-prefixed series, an initials-and-number series, a zero-padded control
range) are named as observation shapes only, per the R2/R4 deferral.

## Sources

`planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment from `make_prompt.py`;
`planning/00-database-agent-product-design.md` (grepped for the spans above, not read in full);
`planning/domains/nodes/law_practice.json` (the schema anchor and its default template, read for the
precondition, never-alone list, `work_types`, template prose and edge idiom);
`planning/domains/nodes/legal.practice-matter-file.research.md` (depth and idiom calibration);
`planning/domains/roster.json` (every edge id verified present: all seven neighbours and the four residual
names); `planning/domains/nodes/construction_property.variation-claim.{json,research.md}` (the one landed
row that had already argued a boundary against this id).

## NEEDS-JOSEPH

- **NJ-EX-1 · The existence question.** Answered as a narrow yes, recorded so it can be reversed. This row
  stands *only* on the designator-plus-schedule pairing and the compilation privacy claim. If R1c judges
  that pairing to be a filename-and-document-type filter rather than a structure, **refuse the row** and
  route the coverage to `law_practice.discovery`, `.trial-preparation`, `.depositions-testimony`, `legal`
  and Protected Records. This row would rather be refused than kept to save an id.
- **NJ-EX-2 · The merge direction, if the `trial-preparation` seam is too fine.** Alternatives: (a) keep
  both, with the bundle on that row and the schedule here — the current proposal; (b) merge **into**
  `law_practice.trial-preparation` and let "schedule of exhibits" be a `work_type` value there; (c) merge
  that row into this one. **(c) is wrong** — the compiled bundle is the larger and better-evidenced
  situation. If a merge happens, it must be (b).
- **NJ-EX-3 · The host-domain rule, which is bigger than this row and which no design document settles.**
  When one file is an exhibit *and* a photograph *and* a medical record: (a) the host domain places it and
  the exhibit namespace is a group only — this row's position; (b) the compiling domain places it and the
  host keeps facts but not placement; (c) the stricter protection places it regardless of either. The row
  assumes (a) plus (c) for protection, marked as inference. This recurs wherever one domain compiles
  another's material (litigation exhibits, grant appendices, planning submissions), so it deserves one
  ruling rather than 36.
- **NJ-EX-4 · Reciprocals owed.** Seven, listed in the boundary table with fixture bytes named on this side
  so each can be checked. Not this agent's to write.
- **NJ-EX-5 · Schema `also_holds_with` gap.** Recommend adding `medical` and `photos` to
  `law_practice.json`'s `also_holds_with`; this row generates both and cannot author them. Cross-row change,
  for R1c.
