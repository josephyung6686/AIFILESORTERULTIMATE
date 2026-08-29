# academic.transcripts-credentials — R1b lab notes

Row: `kind: template`, `schema_id: academic`, `launch: placeholder`, `provenance: inference`.
Verdict: **node stands** (`refuse_node: false`).

## Sources used

- `planning/00-database-agent-product-design.md` — read in full; the authority. Every span in quote
  marks in the node file was grep-verified against this file before it was written (50 spans,
  all present verbatim, including the curly apostrophes in *domain’s* and *user’s*).
- `planning/domains/_CONTRACT.md` — entry shape, rules 8, 11–15.
- `planning/domains/CONNECTION.md` and `CONNECTION-EXAMPLES.md` — both present and binding.
- `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — confirmed my id, kind, schema_id, neighbours; every edge target
  checked against the roster's 83 ids.
- `planning/domains/canonical_fields.json` — `school`, `term`, `subject`, `work_type` (all
  `destination_eligible: true`), `instructor` (not eligible), `target_university`, `target_school`.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`; also the reason one `never_alone` entry
  exists (see below).
- Neighbour nodes already landed and read to align, not rewrite: `academic.json`,
  `academic.coursework.json`, `academic.continuing-education.json`, `academic.online-course.json`,
  and greps of `college_applications.json` and `career.json`.

I did not open `planning/deferred-catalogues/`: nothing in this node's recognition consumes an
existing catalogue. The gazetteer it leans on is R4's schools list, named as a rule family only,
with no contents invented here.

## Node test — why this is not the schema's default template

All three legs differ from `academic.coursework`, and the middle one is the substantive difference.

1. **Detection signals.** Coursework fires on a course-code-plus-context pair describing the
   document itself. This situation fires on *issuer-and-attestation* structure: a registrar or
   awarding-body heading, a seal or signature-block caption, a verification or document-id slot,
   degree-conferral or credit-award language. A transcript can contain no context term at all in
   coursework's sense and still be unmistakable.
2. **Recommended dimensions.** `school → work_type`, not `school → term → subject → work_type`.
   The two dimensions coursework leans on are the two this material cannot supply: an official
   record enumerates many courses across many terms inside one file, so a single `subject` or
   `term` value would be invented rather than read. `00`'s own discipline points the same way —
   *"A course code alone should not merge different semesters; course packet identity should
   include a term when it is available"* — and here the file carries all of them. The single-term
   grade report (fixture `Spring 2026 grade report.pdf`) is the exception, and it is recorded as an
   optional branch pattern, not as the default.
3. **Privacy rules.** This is the grade-bearing and credential-bearing corner of the Academic
   schema; it is the one academic situation whose fallthrough set includes **Protected Records**,
   because `00` lists *credentials* inside that residual's own definition. A `privacy_rules` block
   is authored for that reason and states what may leave the device (a heading and an award line,
   never a grade table), citing `00`'s minimisation sentence.

None of the three differences is a work type or a file extension.

## Files considered and rejected

- **`Diploma frame.psd` / a design file of a certificate template.** `design_creative` with a
  credential-shaped name, but it is a template someone is *making*, not a record someone was
  *issued*. It would have added a `SOURCE_TYPE` and no new discrimination; the AWS certificate
  fixture already carries the "credential-shaped page that is not this situation" job.
- **`Diploma.docx` drafted by the school before issue.** Same shape as the issued PDF minus the
  attestation. Interesting, but it collapses to the same `never_alone` entry (a seal or letterhead
  alone attests nothing), so it earned no slot.
- **A `.vcf` of a registrar's contact card.** `00` settles it outright: contact data *"should
  normally be privacy-protected rather than used to create folder proposals"*, so it can never be
  this template's file. Rejected as a fixture rather than argued in the node.
- **A LinkedIn "add to profile" certificate link email.** Nearly identical to the transcript-order
  email fixture and weaker; one transactional-email fixture is enough.
- **`Study abroad credit approval.pdf`.** Genuinely on the `academic.study-abroad` seam, but that
  node has not landed and I would be writing its half of a collision blind. Left out; noted below.
- **A degree-audit HTML export.** Kept the *degree audit* value in `work_types` and dropped the
  file, because the interesting property (issuer attestation absent, course rows present) is
  already carried by the unofficial-transcript screenshot fixture and named in `needs_llm`.

Twelve fixtures survived, covering: labelled/structured record, unlabelled prose-adjacent record,
OCR of a scan, OCR of a screenshot of the same kind of thing, a camera photograph of the same,
a password-protected archive packet, a spreadsheet, an email, two collision fixtures that *look*
like this node and belong to neighbours (`career.credentials-licenses`,
`finance.student-financial-aid`), one that looks like it and belongs to `research`
(`Interview transcript …`), and one that is *also* another schema (`Transcript.pdf` in a packet).

## `proposed_fields` — none

The five inherited academic keys carry every fact this situation can establish: `school` (the
issuer), `work_type` (which record), and `term`/`subject` in the narrow single-term case.
`instructor` stays search-side and not destination-eligible.

Three candidate fields were considered and rejected as **values or as another domain's**:

- `issuing_institution` — this is `school` in its ordinary role. Minting it would be exactly the
  574's failure mode (a second spelling of a shared key), and CONNECTION licenses a near-duplicate
  only for a genuine role split, which this is not: the role split that *is* real here
  (`school ↔ target_university`) already exists in the canonical list and is referenced, not minted.
- `credential_type` — a synonym for `work_type` whose members (*transcript*, *diploma*,
  *enrollment verification*) are values. `00`: *"The system may create new values when it sees a
  new course, project, company, university, or event, but it should not invent new fields
  automatically."*
- `verification_code` / `document_id` — a strong **detection signal** and a terrible field: it is a
  per-document identifier that would populate a folder level with one child per file, and it is
  credential-bearing text that should not be widened into a stored, displayable dimension. It stays
  in `recognition.deterministic` and in a `never_alone` entry (a code with no issuer proves nothing).

## The `never_alone` entry that matters most

`transcript` in a filename. This node's tempting false file is not a near-miss academic document —
it is an interview, deposition, podcast or caption transcript, and `transcript` is *also* the name
of an evidence zone and a plausible `audio_video` artefact inside this product's own extraction
shape (`src/evidence_shape/vocabulary.py`: `ZONES` ends `"manifest", "ocr", "transcript"`). A rule
that fired on the word would mislabel research interview material as an academic credential, which
is why fixture `Interview transcript - Prof Nakamura 2026-03-04.docx` is in the file list with
`facts_legal: []`.

## Neighbours considered that did **not** get an edge

- **`academic.teaching`** — a teaching-side file is authored *about* other people; it is not an
  issued record about the holder, and no single evidence item plausibly supports both. The seam
  that does exist (a gradebook vs a transcript) is already discriminated on the coursework edge.
- **`academic.k12-schooling` / `academic.iep-accommodation-plans`** — a report card is genuinely
  this situation's shape at K-12 scale, and I expect a real collision there. Neither node has
  landed. Rather than author a one-way edge into an unwritten neighbour's territory and pre-empt
  its own reading, I left it out and flagged it for R1c below.
- **`academic.study-abroad`** — credit-transfer paperwork sits on the seam (my
  `Transfer credit evaluation - Columbia.xlsx` fixture is arguably its file too). Same reason as
  above: node not landed. Flagged for R1c.
- **`applications.graduate-professional` / `applications.scholarship-fellowship`** — the same
  transcript-in-a-packet confusion as `applications.undergraduate-packet`, discriminated by exactly
  the same evidence. One collision edge carries the discrimination; three would be the same signal
  restated, and R1c can fan it out if reciprocity wants it.
- **`career.recruiting`** — a transcript inside a recruiting packet is the *co-holding* case, not a
  confusion: recruiting evidence (a role, an employer, an offer) is disjoint from issuer
  attestation. The `academic ↔ career` co-holding is already asserted on the schema rows, so this
  template adds nothing.
- **`medical.*`** — an immunization record is issued by a health provider even when a school
  demands it. No academic issuer, no academic fact; not this node's material.

## Where CONNECTION overrode the dispatch prompt

The prompt lists `also_holds_with` as an edge I may author. `CONNECTION.md` §5 restricts it to
**schema ↔ schema only**, and CONNECTION wins. So `also_holds_with` is `[]` here with a note, and
the co-holding this situation depends on is carried two ways instead: through
`file_examples[].also_schema` (`college_applications`, `photos`, `identity`, `research`) and by the
schema-level edges `academic.json` and `college_applications.json` already assert. `parent_id` is
`null` and was never authored (PR-5). `shares_field` is never authored anywhere.

I also followed the sibling templates' serialization for `falls_through_to` (objects carrying
`residual_template` / `why` / `provenance`) rather than the bare-string form the prompt's skeleton
shows, so this row merges consistently with `academic.coursework`, `academic.continuing-education`
and `academic.online-course`. All seven targets are `00`'s residual names, spelled `00`'s way.

## Reciprocity owed to R1c

- `academic.coursework` → already names this row; **reciprocated** here in matching terms.
- `academic.continuing-education` → already names this row; **reciprocated** here, in its own words.
- Owed *to* this row, one-way today: `academic.standardized-testing`,
  `career.credentials-licenses`, `applications.undergraduate-packet`,
  `finance.student-financial-aid`, `identity.core-documents`.
- Not authored, needs a decision: `academic.k12-schooling`, `academic.iep-accommodation-plans`,
  `academic.study-abroad`.

## NEEDS-JOSEPH — this node only

**NJ-T1 · What is the default home for a transcript that serves several packets and names no
institution of its own?** Recorded as the node's `open_question`. `00` poses the fork and refuses
to settle it: the frozen tree *"should therefore include a policy for shared material: a shared
branch, a primary-home convention, a reference or alias convention, or mandatory review"*; it names
`Applications/Shared Application Materials` as one such branch; and it forbids the system from
choosing — *"If no shared branch exists, the system should not arbitrarily choose one university.
It should abstain or ask the user to choose a primary home."* What `00` does not say is which home
the product should *offer first*, before the user has expressed any preference: this template's
Academics branch (the record's issuer) or the Applications shared-materials branch (the record's
use). The answer changes what a user sees on their very first pass, so it is Joseph's, not R1's.

Explicitly **not** re-raised here: whether `potentially_sensitive` attaches to the whole Academic
domain or only to its grade-bearing work types. That is already the `academic` schema row's open
question and duplicating it would double-count one fork.
