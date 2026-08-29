# academic.teaching — lab notes

Row: `kind: template`, `schema_id: academic`, `launch: placeholder`, `provenance: inference`.
Verdict: **not refused.** Reasons below.

## Sources used

- `planning/00-database-agent-product-design.md` — read in full; the authority. Every span this
  node puts inside quote marks was matched against it with `grep -F` **before** it was written,
  and re-verified mechanically after writing (20 quoted spans, 0 unverified).
- `planning/domains/_CONTRACT.md` — entry shape, rules 8 (snake_case + a dimension may only
  branch on a declared field), 11–14 (kinds, `uses_schema`, browse-only `parent_id`, closed edge
  vocabulary), 5 (sensitivity phrase only, no handling class).
- `planning/domains/CONNECTION.md` — §2 node test, §4 activation (never-alone as an edge
  invariant, the grouping firewall), §5 the closed edge vocabulary and its between-columns,
  §7 four objects / four owners, **PR-7** (teaching vs taking is one Academic schema; a second
  template on the same schema is the licensed form).
- `planning/domains/CONNECTION-EXAMPLES.md` — fixture 7 is this row, by name. It records
  `tpl.academic-teaching` with `dimension_order: ["term", "subject", "work_type"]` and the note
  that "differs in detection signals and recommended dimensions" is what licenses the row. This
  node adopts that order (see the tension below). Fixtures 3, 5 and 6 shaped the `never_alone`
  list and the sparse-file example.
- `planning/prompts/ALIGNMENT.md` — work types are values; a template that only repeats its
  schema's default is not a node.
- `planning/domains/roster.json` — confirmed id, kind, `schema_id`, neighbours, and every edge
  target. Note this row carries no `file_kind_owner` in the roster (coursework owns
  `text_document` / `calendar` / `presentation`), so `file_kinds` here is stated as plausibility
  only, `never_alone: true`.
- `planning/domains/canonical_fields.json` — no new keys needed; `fields: []` because a template
  references its schema.
- `planning/domains/nodes/academic.json` — the schema row, already landed. Its five fields,
  their reliability ceilings, and its `also_holds_with` edges are read, not rewritten.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked programmatically against every
  `file_examples.source_type` and every `file_kinds.source_types` member.

`planning/01-product-design-structured.md` was not opened: `00` covers every claim here and wins
on conflict, and the reading-economy instruction limits 01 to sections the prompt cites.

## Why this row survives the node test

CONNECTION §2 refuses a template whose detection signals, recommended dimensions **and** privacy
rules all match its schema's default. Three differ, independently:

1. **Privacy rules.** Coursework is about the holder's own work. Teaching holds *other people's*
   data as a matter of course — rosters, gradebooks, submission archives, evaluation comments,
   platform screenshots showing student rows. That is a different constraint on what may be shown
   in a canvas or sent to a model, and it is why `Protected Records` is a fallthrough here and not
   on the coursework side.
2. **Detection signals.** The artifacts themselves do not discriminate — a syllabus PDF is the
   same bytes on both sides. What discriminates is *authorship and cohort custody*: a labelled
   Instructor slot resolving to the holder, a grading-policy or office-hours section the file sets
   rather than reports, a rubric / answer key / exam master, a many-student roster or gradebook, an
   ICS whose ORGANIZER is the holder. None of these appears in the schema's default signal set.
3. **Recommended dimensions.** `school` is dropped (one employer → a one-child level), leaving
   `term → subject → work_type` against coursework's `school → term → subject → work_type`.

Had only (3) held, I would have refused: dropping one level is thin. (1) is the substantive one —
it changes what the product may *do* with the branch, not only how it is shelved.

I did **not** propose a second schema. PR-7 forbids it and fixture 7 names the forbidden row
(`acad.teaching` with `["school", "term"]`) explicitly. `fields` is empty and the node relies on
`schema_id: academic`.

## Files considered and rejected

- **`students.vcf`** (a section's contact export). Rejected as an example because `00` settles it
  outright — contact data "should normally be privacy-protected rather than used to create folder
  proposals" — and CONNECTION fixture 6 already treats `.vcf` as `{}` for placement purposes. It
  survives only as a `never_alone` entry: a many-person-names table looks identical whether it is a
  class roster or an address book.
- **`Course reserve reading - Chapter 4.pdf`** (a scanned chapter the instructor posts). Rejected:
  its only teaching evidence is the folder it sits in, and it is indistinguishable from the
  student's copy of the same scan. It is a `Reading Inbox` file until a course token appears.
- **`Zoom recording 2026-03-02.mp4`** (`audio_video`). Rejected: transcripts are gated behind
  "an explicit privacy and compute policy" in `00`, so the file yields duration and container
  metadata and nothing that could reach a course fact. Including it would have implied a transcript
  pipeline this node cannot assume.
- **`Payroll - March 2026.pdf`**. Rejected as an example: it is a `finance` / `career` file that
  merely shares the employer. It informed the `career.employment-records` collision instead.
- **`Accreditation self-study.docx`** (departmental, names many courses). Rejected: no single
  subject value is recoverable, which is the same defect as the transcript's many-course table in
  the schema node. It would have taught the wrong lesson twice.

## proposed_fields justification

**None proposed.** Two candidates were considered and rejected:

- **`section`** (a course's parallel sections, and the column that appears in every roster). It is
  a *value-shaped* discriminator inside one course, and a section-level folder is exactly the split
  `00` asks the canvas to warn about — a level that "creates a large number of tiny folders."
  Minting a key so a dimension could exist would be the failure `_CONTRACT` rule 8 names ("Do not
  invent fields to make the gate green").
- **`cohort` / `enrollment_count`**. Search-side at best, and a count is a number, which this
  catalogue may not hold.

The instructor-side artifacts (rubric, answer key, gradebook, class roster, submission packet) are
**values of `work_type`**, listed in `work_types[]`. That is ALIGNMENT's rule and it is what keeps
this row from becoming eight more rows.

## Neighbours considered that got no edge, and why

- **`also_holds_with` is empty by contract, not by omission.** CONNECTION §5 restricts that edge to
  **schema ↔ schema**. This row is a template, so it cannot author one — even though the
  co-holding is real (a course evaluation is teaching material *and* career material; a
  recommendation letter is teaching-adjacent *and* an application document). The dispatch prompt
  invites `also_holds_with` on any node; **CONNECTION wins and is followed here**, and the
  co-holding is recorded where a template legitimately can record it: `file_examples[].also_schema`
  (`career` on the evaluations report and the teaching statement, `college_applications` on the
  recommendation letter). The schema-level edges already exist on `academic.json`
  (`academic ↔ career`, `academic ↔ research`, `academic ↔ college_applications`); nothing here
  needs re-authoring, and this node did not touch that file.
- **`college_applications` (schema) / `applications.*` (templates).** No collision authored. The
  confusion a teaching file could have with an application is mediated by the recommendation-letter
  situation, which already carries the edge; adding a second path for the same evidence would be
  two edges for one discriminator.
- **`academic.transcripts-credentials`.** Considered and dropped. A transcript is issued *to* a
  student; the teaching side never holds one about itself. The near-miss is a grade *report* the
  instructor submits to a registrar, which is a `gradebook` value here, not a transcript.
- **`academic.homeschool`.** Genuinely close — the holder teaches and administers at once — but the
  discriminating evidence is the same one the K-12 edge already carries (one named child versus a
  cohort), and homeschool's own row is the better place to state it. Left to R1c reciprocity rather
  than duplicated here.
- **`career.employer-side-hiring`.** Rejected: a hiring panel's rubric and a course rubric share
  the word and nothing else — no course token, no term pattern, no cohort. That is a word
  collision, and `00` already forbids substring reasoning ("It should use word-boundary matching
  rather than substring matching").
- **`role_split` is empty.** There is a real observation behind the temptation: on a teaching file
  the `instructor` value and the file's author are usually the same person, which is precisely the
  collapse `00` warns about when it says to "avoid using authorship or creator identity as a
  destination dimension." But `role_split` lives on the **canonical field list** (CONNECTION §5–6)
  and `canonical_fields.json` records no `instructor ↔ authored_by` pair. Authoring one from a
  template row would be minting a field-graph edge from the wrong place. Recorded below instead.

Reciprocity for all five `collides_with` edges is R1c's merge job; this node authored only its own
direction, as instructed.

## Tension recorded, not silently resolved

`dimension_order` is `["term", "subject", "work_type"]`, taken from CONNECTION-EXAMPLES fixture 7
and consistent with `00`'s own Academic sentence ("An Academic template may define school → term →
course → work type"). But `00` also says, of document and record domains generally, that "project,
function, or subject usually comes before time because putting year first scatters related work
across calendar folders." For a teacher who re-teaches one course for a decade, `subject → term`
is arguably the better retrieval order and would keep one course's material together. Both
sentences are `00`'s; neither is wrong. The node follows the fixture, states the alternative in
`template.why`, and leans on `00`'s own escape hatch: "The system recommends an order based on the
domain template, but the user can reverse, remove, add, or flatten dimensions." Flagged so R1c can
see it was a decision and not an oversight.

## NEEDS-JOSEPH (this node only)

1. **Does a teaching branch default to protected?** Rosters, gradebooks, submission archives and
   evaluation comments carry named students and their grades. Defaulting the whole situation to
   protected gates an instructor's ordinary course files out of model review; defaulting only some
   work types makes protection depend on `work_type`, a fact that is itself only `validated`, and a
   roster named `students.xlsx` slips past it. Carried in the node's `open_question`.
2. **Does the teaching recommendation keep `school`?** Dropped here as a one-child level, which is
   right for a full-time instructor and wrong for an adjunct teaching at two institutions. The user
   can add the level back; the question is what the *default* should be. Carried in the same
   `open_question`.
3. **Should `instructor ↔ authored_by` become a canonical `role_split`?** Not this node's to add,
   and not urgent — `instructor` is already `destination_eligible: false`, so no folder level
   depends on the answer. Raised here because this is the situation where the two roles collapse
   onto one person and a future reader will notice.
