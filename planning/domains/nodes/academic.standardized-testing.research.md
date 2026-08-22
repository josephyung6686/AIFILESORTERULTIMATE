# Lab notes — `academic.standardized-testing` (R1b, kind: template, uses schema `academic`)

Date: 2026-08-22
Node file: [`academic.standardized-testing.json`](academic.standardized-testing.json)
Verdict: **not refused.** The node test passes on two independent grounds, recorded below.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node
  file was grep-verified against this file before it was written; the verification pass is
  reproducible by extracting the double-quoted spans from the JSON and substring-matching them
  against `00`. Eighteen distinct spans, all present verbatim.
- `planning/domains/_CONTRACT.md` — entry shape, rules 8 and 11–15.
- `planning/prompts/ALIGNMENT.md` — the two-kind split; "work types are values"; template ≠ schema.
- `planning/domains/CONNECTION.md` — node test (§2), closed edge vocabulary (§5), field identity
  (§6), the activation algorithm's never-alone step (§4.2), the grouping firewall (§4.9).
- `planning/domains/CONNECTION-EXAMPLES.md` — checked for the `also_holds_with` fixtures only.
- `planning/domains/roster.json` — confirmed `kind: template`, `schema_id: academic`,
  `launch: placeholder`, `provenance: inference`, `inherited_field_keys`, and that every edge
  target below is a real roster `domain_id`.
- `planning/domains/canonical_fields.json` — `school`, `term`, `subject`, `instructor`,
  `work_type` re-read in full, including each row's `role` sentence and `destination_eligible`.
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — every `file_examples.source_type` checked
  against the closed fourteen.
- Landed neighbour nodes, read to align edges without rewriting them:
  `academic.json` (the schema), `academic.coursework.json`, `academic.continuing-education.json`,
  and the collision rows of `academic.iep-accommodation-plans.json` and `academic.online-course.json`.
- **Not used:** `planning/domains/01-education-academia.md`. The legacy 574 contains an
  `acad.standardized-testing` row recommending `test → test_sitting → testing_record_type`. That
  row is superseded by R1's roster, and its three private field names are the exact failure mode
  this pass exists to avoid — noted here only so the next reader knows it was seen and rejected,
  not silently reproduced.
- No `planning/deferred-catalogues/` entry was consumed: recognition here needs a test-name
  gazetteer that does not exist yet, and inventing its contents is R4's job, not this node's.

## Why the node test passes

Two grounds, either sufficient on its own:

1. **Detection signals differ from the schema's default template.** `academic.coursework` fires on
   a course-code-shaped token beside one of `00`'s five academic context terms. Nothing in this
   situation produces that pair. What fires here is a test name beside a score-report, registration
   or prep structure — a labelled scaled-score-plus-percentile-plus-test-date triple, an
   appointment identifier with a test center, a numbered timed item set with an answer key.
2. **The recommended dimensions differ, and differ by subtraction.** The schema recommends
   `school → term → subject → work_type`. This node recommends `subject → work_type` and drops the
   other two for two different, specific reasons (below). A recommendation that halves the
   schema's depth is not the schema's default template.

The privacy rules also differ in kind — a score report prints a date of birth and a candidate
identifier, and one routine member of this situation cites a diagnosis — but the node does not
lean on that, because the Academic schema is already `potentially_sensitive`.

## The two dropped dimensions — the reasoning, in full

**`term` is dropped, not demoted.** `term`'s validating rule family is the dedicated
academic-term pattern (`00`: *Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term
2024 require dedicated patterns rather than generic parsing*). A test date is a calendar date, not
a term, and `00`'s narrow-date rule exists precisely so a date-shaped token does not become a term.
Branching on a field no rule can fill would open a level that produces empty branches — `00`'s own
validation constraint.

**`school` is dropped for a role reason, not an evidence reason.** The canonical `school` row's
`role` reads *the institution the holder attends, attended, or teaches at - the person's own
school, never the application target* (quoting `canonical_fields.json`, not `00`). A testing
organization administers and scores; it neither teaches nor enrols
the holder. The universities on a score-recipient list are application targets, which is
`target_university`'s role and not this schema's field. The high school a candidate attended at the
time of a sitting is printed on some reports, but branching on it scatters one test's material
across institutions and is a `00`-style flatten case.

This is where the node diverges from its sibling `academic.continuing-education`, which does use
`school` as its first dimension: a CE provider **teaches** the holder, so the `school` role fits
there and does not fit here. Recording the difference explicitly, because the two rows otherwise
look like the same shape and a merger pass could reasonably assume they should match.

## Files considered and rejected

- **A university's own placement or proficiency exam** (a departmental language placement test).
  Rejected: it is administered by the school as part of enrolment, carries a course-code or
  enrolment context, and lands on `academic.coursework`. Including it would have made the
  test-name-plus-testing-structure signal look weaker than it is.
- **A driving-theory or citizenship test result.** Rejected: real, but its record is a
  government-issued entitlement, and treating it here would pull identity-domain material into an
  academic template on the strength of the word *test* alone.
- **A school-issued standardized assessment report about a child** (state testing sent to a
  parent). Rejected as a fixture for this node: `academic.k12-schooling` owns the holder-is-parent
  situation and its research notes already say so. Left to that node rather than fought over.
- **An employer's pre-hire aptitude assessment result.** Rejected: the sitting shape matches, but
  the file's purpose is a recruiting process, and `career.recruiting` owns it. Not given an edge
  either — see below.
- **A proctoring-software installation receipt.** Rejected as noise: it is a software artifact
  whose only testing signal is a vendor name.

## `proposed_fields` — none, deliberately

Two fields would genuinely improve this situation and neither was proposed:

- **the sitting** (test name + administration date as one identity). It is what a repeat test-taker
  browses by, and the "one sitting and everything it produced" grouping reason has no field to hang
  on without it. `term` cannot hold it (rule family mismatch, above).
- **the testing organization.** No canonical key has the right role: `school` is the holder's own
  institution, `target_university` is an application target, `institution` is the finance schema's
  record-issuer and is not a field the Academic schema declares, so a dimension on it would be
  illegal under `_CONTRACT.md` rule 8 regardless.

Both are recorded in `open_question` instead. Minting `test_sitting` and `testing_body` is exactly
the 2,295-private-names failure the canonical list exists to prevent, and a template row is the
weakest possible place to introduce a field. If Joseph wants the sitting level, the decision is a
canonical-field decision, made once, for every node that needs it.

A third question is recorded with them and is arguably prior to both: **whether a test name is
legitimately a value of `subject` at all.** The roster row instructs it and this node built on that
instruction, but `subject`'s canonical role is *the course or study subject the material belongs
to* (`canonical_fields.json`, not `00`), and a test is a target
rather than a course of study. If that reading is rejected, this template loses its first dimension
and reduces to `work_type` alone — which would fail the node test and make the row a refusal. That
is stated plainly in `open_question` rather than smoothed over.

## Edges — what was authored, and what was not

**Authored `collides_with` (template ↔ template, per CONNECTION §5):**

| Target | Why |
|---|---|
| `academic.coursework` | reciprocates an edge that node already states; the two halves are `PHYS1401 Midterm Practice.pdf` and `Practice Test 4.pdf` |
| `academic.iep-accommodation-plans` | reciprocates an edge that node already states; issuer and scope discriminate, the mutual citation does not |
| `academic.transcripts-credentials` | both are official result records with a verification identifier; grades-and-conferral versus one administered test |
| `career.credentials-licenses` | the sitting half versus the licence half; `Bar_Exam_Results_Letter.pdf` carries both and is an abstention case |
| `applications.undergraduate-packet` | a score report inside a packet; the score-recipient list is not target-institution evidence |

**`also_holds_with` is empty — and this is a deliberate departure from the roster hint.** The
roster's `one_line_hint` says *consider also_holds_with college_applications*. CONNECTION.md §5
restricts `also_holds_with` to **schema ↔ schema only**, and this row is a template. The dispatch
prompt's edge table permits `also_holds_with` without that restriction; per the prompt's own
tie-break, **CONNECTION wins and this is the note recording it.** The substance the hint wanted is
not lost: `academic.json` already asserts `also_holds_with` toward `college_applications`, with the
transcript-in-a-packet case as its signal, so a score report inside an application packet
co-activates correctly at the level where co-activation is decided. The template-level fact — that
the same document is confusable from both sides on one evidence item — is carried by the
`applications.undergraduate-packet` collision instead, which is the right edge for that job.
`file_examples[0].also_schema = "college_applications"` records the per-file reading.

**Neighbours considered that got no edge:**

- **`academic.online-course`.** Prep courses are sold on platforms and a platform completion
  certificate can sit beside practice sets. No edge: the online-course side is evidenced by a
  platform enrolment and a completion, this side by a sitting or a score, and no single evidence
  item supports both. A collision edge here would mean *these look adjacent*, which is not what
  the edge means.
- **`career.recruiting`.** A pre-hire aptitude assessment result is a real confusion, but the
  discriminating evidence is a hiring process the recruiting node owns end to end, and asserting a
  mutex on a file shape this node does not otherwise claim would be inventing a collision to look
  thorough.
- **`academic.k12-schooling`.** State assessment reports overlap, but that node's own notes say it
  defers this situation to this one; adding a mutex back would create a reciprocity obligation on a
  node that has already reasoned its way out of the overlap.
- **`medical` (schema).** Reached only through `file_examples[9].also_schema` — the accommodations
  approval cites a diagnosis, so the medical safety schema co-activates for protection. That is a
  schema-level co-activation and a template row cannot author it; it is noted here so a merge pass
  can decide whether `academic ↔ medical` deserves an `also_holds_with` at schema level. It does
  not follow from this node alone.
- **`finance.receipts-expenses`.** A registration confirmation carries a fee and a card fragment.
  No edge: the file falls through to Receipts and Confirmations when nothing else fires, which is
  the mechanism `00` provides for exactly this, and a residual home is not a domain.

**`role_split` is empty.** The `school ↔ target_university` split is the schema's and is already
recorded on `academic.json` and in the canonical field list. Restating it here would duplicate a
schema-level assertion on a template row.

## Sparse-file and grouping discipline

`Practice Test 4.pdf` is this node's `HW 3.pdf`. It reaches `work_type` from its own structure and
nothing else — no `subject` from the score report next to it, no `school`, no `term` — and carries
`group_without_copying_facts: true`. Three other fixtures do the same for different reasons: the
archive (`test_prep.zip`) has only a manifest, and the photographed score slip (`IMG_3391.HEIC`)
has no text layer until OCR re-runs recognition under a new cache key. Activation and grouping stay
separate throughout: a file may join a testing neighbourhood without this template's signals ever
firing on it.

Every `file_examples` entry lists `a folder path` first in `must_not_conclude`, because the one
error that would survive review unnoticed is a path written as a fact.

## NEEDS-JOSEPH (this node only)

- **NJ-ST-1 · No field holds a test sitting, and none holds the testing organization.** `term` is
  validated by the academic-term rule family and cannot hold a test date; `school` is the wrong
  role for a body that administers and scores but neither teaches nor enrols. A repeat test-taker's
  real browse dimension is therefore unavailable, and the "one sitting" grouping reason has no
  field. Decide at the canonical-field level or accept a two-level template permanently. This node
  proposed no field rather than mint one.
- **NJ-ST-2 · Is a test name a legitimate value of `subject`?** The roster instructs it; the
  canonical role sentence for `subject` (*the course or study subject the material belongs to*)
  arguably does not cover a
  test. A "no" answer collapses this template to a single dimension and turns the row into a
  refusal, so the answer decides whether the node exists.
- **NJ-ST-3 · Does a testing-accommodations approval belong here or with the safety domains?** The
  node routes it to Protected Records on fallthrough and marks `also_schema: medical` on the
  fixture, but which part *surfaces* a protected record is CONNECTION's NJ-4, still open. Nothing
  in this row depends on the answer.
