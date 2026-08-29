# Lab notes — `applications.k12-admission`

Date: 2026-08-22 · R1b, one roster row · `kind: template` on `schema_id: college_applications`
Verdict: **node stands** (`refuse_node: false`). Reasons under "Node test" below.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node
  JSON was grep-verified against this file before it was written: 33 distinct quoted spans, all
  present verbatim. The one remaining quoted span in the JSON
  (`"the same organizational situation covers targets that are not universities"`) is attributed
  in-line to `college_applications.json`'s own `open_question`, not to `00`, and is verbatim
  there.
- `planning/01-product-design-structured.md` — §7.3 only, to confirm the nine residual names'
  spelling. No other section needed; `00` was the authority for everything else.
- `planning/domains/_CONTRACT.md` (entry shape, rules 8/11–15), `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md` (§2 node test, §3 no inheritance, §5 closed edges, §6 fields),
  `planning/domains/CONNECTION-EXAMPLES.md` (fixtures 2, 3, 6 are the ones this node has to stay
  compatible with).
- `planning/domains/roster.json` — confirmed `kind: template`, `schema_id: college_applications`,
  `launch: placeholder`, neighbours `academic` + `identity`, residual `Independent Records`.
- `planning/domains/canonical_fields.json` — every field named in the node resolves to a key here.
  No new key was minted.
- `planning/domains/nodes/college_applications.json` — the schema this template points at; its
  five declared fields, its default `dimension_order`, its `never_alone` list and its
  `open_question` are all load-bearing for what follows.
- `planning/domains/nodes/academic.k12-schooling.json` — the closest neighbour, already landed.
  Its `collides_with` already names `applications.k12-admission` and its `role_split` already
  points `school ↔ target_university` at this node. Both are reciprocated here, in its words, and
  its file was not touched.
- `src/evidence_shape/vocabulary.py` — every `source_type` used is one of the fourteen.

## Node test — why this is not the schema's default template

CONNECTION §2 refuses a template whose detection signals, recommended dimensions **and** privacy
rules all match its schema's default. All three differ here, and the third is the strongest:

1. **Detection signals.** None of the college_applications default's discriminators are the ones
   that fire here. This situation is recognised by an entering-grade slot, an entry-year slot, a
   parent/guardian-as-applicant-of-record slot, a Current School slot, a confidential
   teacher-evaluation rating grid, a school-visit or shadow-day event, a physician-completed
   health form, and a household tuition-assistance statement. Conversely, the default's own
   strong signals (a supplemental-essay prompt authored by the applicant, an undergraduate/major
   slot, a common-application shape) are absent or misleading.
2. **Recommended dimensions.** The default is target → cycle → document type. Here the cycle level
   is dropped, because a K-12 admission season is normally one entry year across several schools,
   so the cycle level would produce exactly one child — the case `00` tells the canvas to warn
   about. The node records when to re-insert it (a second season, or two siblings applying in
   different years) rather than deleting the possibility.
3. **Privacy rules — the decisive one.** The default assumes applicant = holder. Here the
   applicant is a **minor who is not the holder**, and the packet's required members are the
   heaviest ones in the product: a child's date of birth and home address on the form itself, a
   physician-completed health record, a household financial statement, and a third-party
   confidential assessment of the child. That is a different privacy rule, not a different flavour
   of the same one, and CONNECTION §2 names privacy rules as an independent licence for a template
   row.

The failure mode this node was watched for — inventing a schema, or a second copy of the schema's
fields, to justify the id — did not occur: `fields` is empty and the node relies on `schema_id`.

## Files considered and rejected

- **`Common App - Activities.pdf`** — rejected as a file example: it belongs to
  `applications.undergraduate-packet` and adding it here would have blurred the very collision
  this node has to keep sharp. The discriminator is recorded as an edge signal instead.
- **`Kindergarten Lottery Result.pdf`** (public-school assignment lotteries) — rejected. Real, but
  the file's evidence is a placement notice from a district, which reads as an enrolled-student
  record once accepted and as an admission decision before; it duplicates the
  `Acceptance Letter.pdf` seam without adding a new observation/fact split. Left out rather than
  padded in.
- **`ISEE Practice Test.pdf`** — rejected. It carries a test-name token and nothing else, so it is
  `academic.standardized-testing`'s and the point it would make is already carried by the
  `SSAT Score Report` example's recipient-block trap.
- **`Tour Photos/IMG_*.HEIC` from a campus visit** — rejected. Camera EXIF makes them `photos`
  material; nothing in a campus photograph evidences an application, and including them would have
  invited exactly the invented association `00` warns against for isolated images.
- **`Boarding School Brochure.pdf`** — rejected. A marketing brochure names a school in a
  high-weight zone and nothing else; it is the `never_alone` school-name case, already covered,
  and its honest home is Reading Inbox.

Kept deliberately as the ugly cases the prompt asks for: a labelled form (`Application for
Admission`), unlabelled prose (`Essay.docx`), the OCR of a portal (`Screenshot …png`) beside the
camera photograph of the same kind of object (`IMG_0912.HEIC`), the archive packet
(`admissions-packet.zip`), calendar (`Shadow Day …ics`), mail (`Re_ …eml`), the neighbour's file
that looks like ours (`Report Card …pdf`, and `Health Form - Emma.pdf`), and the files that are
**also** another schema without being a collision (`SSAT Score Report` → academic,
`Fifth Grade Transcript` → academic, `PFS Summary` → finance, `IMG_0912.HEIC` → photos).

## `proposed_fields` justification

One proposal, `student`, and it is deliberately a **second sighting of an existing proposal**
rather than a new one: `academic.k12-schooling` proposed the same key for the same gap from the
enrolled-child side. Filed here so R1c has corroboration that one household-shaped field is
missing, and explicitly flagged so R1c merges rather than creating two columns — which is the
exact defect D6's ratification exists to kill.

The gap is concrete and not cosmetic: a household applying for two children in the same season has
no declared field separating the two packets, and every high-weight signal this template has
(target school, entering grade, entry year) can be identical across them. It is therefore **not**
placed in `dimension_order` — a template may only branch on fields its schema declares — and the
node's `template.why` says out loud that its recommended order omits the level the household
actually files by.

**`entry_grade_level` was considered and NOT proposed.** For one child in one season it is
one-to-one with `application_cycle`, so as a folder level it would produce exactly one child. It
is a strong *detection signal* and a *value* inside a labelled slot; it is not a field this
situation needs, and minting it would have been the "one more field to look thorough" move.

Nothing else was proposed. `instructor` was explicitly **not** requested for the teacher-evaluation
case: the evaluating teacher is not teaching a course to the holder, `college_applications` does
not declare `instructor`, and `00` keeps person-identity off destinations anyway.

## Neighbours considered that did NOT get an edge, and why

- **`identity` (a `must_consider_neighbors` entry).** No edge, on purpose. `collides_with` joins
  **same-kind** pairs only and `also_holds_with` joins **schemas** only (CONNECTION §5), so a
  template row cannot legally point at the `identity` schema in either direction. The substance is
  preserved where it belongs: the `Application for Admission` example carries
  `must_not_conclude: "identity-schema activation from a date-of-birth slot alone"`, matching
  `academic.k12-schooling`'s handling of the same slot, and `college_applications` already holds
  the schema-level `also_holds_with → identity` for the packet that genuinely contains an ID
  document. Where the prompt's edge table implies a template may write `also_holds_with`,
  **CONNECTION wins and `also_holds_with` is left empty** — noted here as the prompt instructs.
- **`academic` (the other `must_consider_neighbors` entry).** Same reason: it is a schema, this is
  a template. The real confusions with academic material are edged at template granularity —
  `academic.k12-schooling`, `academic.standardized-testing`,
  `academic.transcripts-credentials`, `academic.recommendation-letters-written` — which is where
  the discriminating evidence actually differs. `college_applications ↔ academic` already carries
  both the collision and the also-holds at schema level.
- **`applications.purpose-packet`.** No edge. It is not a competing recognition of the same
  evidence; it is the *flat purpose-defined packet* branch pattern (`00`'s Chinese University
  Application Materials shape) available to any applications situation, including this one. A
  collision edge there would say "do not treat one as the other", which is false — a family may
  legitimately keep this season as one flat purpose folder.
- **`applications.graduate-professional`.** No edge. The applicant-role markers that separate it
  from this template are the same ones already spelled out against
  `applications.undergraduate-packet`, and a third near-identical signal would be noise rather
  than discrimination.
- **`legal.personal-legal-matters`.** Considered because custody and guardianship documentation
  can be requested by an admitting school, and `academic.k12-schooling` does carry that edge. Not
  edged here: a custody order's own evidence (court caption, docket number, notarisation) never
  looks like an admission document, and the requirement clause naming a school is already covered
  by the `Health Form` fixture's rule that a school name in a requirement clause is not an
  addressee. Recorded rather than edged so R1c can add it if it disagrees.
- **`academic.iep-accommodation-plans`.** Considered and not edged for the same reason: a learning
  -support disclosure inside an admission form is a slot value, not a competing document identity.
  The neighbour already edges the enrolled-side confusion, which is the one that actually exists.
- **`falls_through_to`.** Four of `00`'s nine, matching what the file examples actually route to:
  Independent Records (the roster's own must-consider, and where a standalone decision letter or
  fee receipt lands), Review Later (the sparse essay, the visit event), Protected Records (the
  health form, the financial statement, the confidential evaluation), Temporary Screenshots (the
  portal capture). Reading Inbox was considered for brochures and rejected — brochures are not
  this template's files at all, so the fallthrough would be describing a file we refused.

**Shape note for R1c.** `falls_through_to` is serialized here as plain residual names, matching
this dispatch prompt's output spec and the `academic.k12-schooling` sibling.
`applications.undergraduate-packet`, landed concurrently, serializes the same edge as
`{residual_template, why, provenance}` objects — the richer form `_CONTRACT.md` rule 6 also
permits. Two shapes are live in the corpus; normalising them is a merge decision, not a
disagreement about which residuals apply, and this node's four are a subset of that sibling's
four. That sibling's `collides_with` already names `applications.k12-admission`, so the pair is
reciprocal in both directions, and its overlap set (`academic.transcripts-credentials`,
`academic.standardized-testing`, `applications.scholarship-fellowship`,
`finance.student-financial-aid`) matches this node's — the two were authored independently and
agree.

## Compatibility check against the R0 fixtures

- Fixture 3 (university name alone → no schema, no group): reproduced as this node's first
  `never_alone`, extended with the one addition this situation forces — a K-12 school name may be
  the child's **current** school as easily as the target.
- Fixture 6 (`HW 3.pdf`, activation ≠ grouping): reproduced as `Essay.docx`, which carries
  `facts_legal: []`, `group_without_copying_facts: true`, and an explicit refusal to take the
  surrounding folder's target school.
- Fixture 2 (one file, two schemas on disjoint evidence): reproduced four times — the score report
  (academic), the transcript (academic), the PFS summary (finance), the photographed form
  (photos). None of them drops the other side's facts, and none of them is written as a collision.

## NEEDS-JOSEPH (this node only)

- **NJ-K12A · The addressee key reads wrong on every file here.** `target_university` is the only
  addressee field `college_applications` declares, and every target in this template is a primary
  or secondary school. This node used the key unchanged — minting a K-12 spelling would be the
  two-columns defect — but the schema already records the same tension as its own open question
  ("the same organizational situation covers targets that are not universities (a scholarship
  sponsor, a program, a secondary school)"). Fork: widen the role of one key while keeping its
  name, or add a second canonical role field. Not decidable at template granularity, and the same
  answer settles `applications.scholarship-fellowship` and `applications.graduate-professional`.
- **NJ-K12B · The missing child dimension, and whether the product should propose it.** No
  canonical field names a record's data subject, so the level this household files by cannot be
  recommended (see `proposed_fields.student`, corroborating `academic.k12-schooling`'s identical
  proposal). Declaring it makes person-shaped folders **for minors** a product-proposed default —
  a privacy decision as much as a filing one. Leaving it out means the recommended order silently
  omits the level that keeps two siblings' packets apart. Joseph's, not R1c's.
