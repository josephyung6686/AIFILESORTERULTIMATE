# R1b lab notes — `academic.online-course` (kind: template, uses schema `academic`)

Date: 2026-08-22
Verdict: **node kept** (`refuse_node: false`). Output:
[`academic.online-course.json`](academic.online-course.json).

---

## Sources used

- `planning/00-database-agent-product-design.md` — read in full; the authority. Every span in
  quote marks in the node file was grep-verified against this file **before** it was written; the
  verification pass re-ran over the finished JSON (17 distinct quoted spans, 17 hits, one
  deliberately fabricated control span failed the same check).
- `planning/domains/CONNECTION.md` (sections 1–7 binding), `CONNECTION-EXAMPLES.md` (fixtures 1,
  5, 6 and 7 are the ones this node has to stay compatible with).
- `planning/domains/_CONTRACT.md` (entry shape; rules 8, 11–14).
- `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — confirmed id, `kind: template`, `schema_id: academic`,
  neighbours, `must_consider_residuals`, and every edge target id.
- `planning/domains/canonical_fields.json` — no key was minted; the three dimensions resolve to
  canonical rows and all three are `destination_eligible: true`.
- `planning/domains/nodes/academic.json` — the schema this template points at. Its fields,
  recognition floor and `never_alone` list were reused, not restated.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked mechanically against every
  `file_examples[].source_type` and against `file_kinds.source_types`.
- `planning/01-product-design-structured.md` — used only as a locator (§2.9 format coverage,
  §3.10 narrow dates, §3.11 domain-scoped schemas, §5.4 / §5.7 templates, §7.3 the residual
  nine). No claim rests on it; `00` wins on every conflict and no § number is quoted as content.
- **Not** consulted: `planning/deferred-catalogues/`. Nothing in this node consumes an existing
  catalogue — the provider list is named as a *rule family* ("a course-provider gazetteer hit,
  R4's content") and no gazetteer member and no regex is written here.

## Why the node test passes

The prompt's refusal condition is a template whose detection signals, dimension order **and**
privacy rules are identical to the schema's default template (`academic.coursework`). All three
differ, and none of the differences is a work type or an extension:

1. **Detection signals.** The dominant evidence in this situation is a *lesson series* — an
   ordinal-prefixed run of `audio_video` siblings with a matching caption file per lesson, which
   is the evidence `00` expects to live *inside* media ("subtitles or captions where present")
   arriving as its own text-bearing file — plus provider-and-completion language. The coursework
   template's signals are registrar / term-pattern / course-code-with-context; none of them
   reaches a captioned lesson series, and the lesson series reaches none of them.
2. **Dimensions.** `term` is dropped from the recommended order, not reordered. Self-paced
   platform study routinely produces no term evidence at all, and `00` admits only dedicated term
   patterns, so keeping the level would open a branch no fact can fill — the thing `00` tells the
   canvas to warn about and flatten. It returns as an **optional branch pattern** for dated
   cohorts, which is `00`'s own template vocabulary ("optional branch patterns").
3. **Privacy contour.** Coursework's sensitivity comes from grades and other people's names. Here
   the bulk of the corpus is published third-party media with no personal content, and the
   personal residue is a named certificate, an order receipt and a mail file. Same enum value
   (`potentially_sensitive`), materially different reason and materially different blast radius —
   recorded in `sensitivity_why` so R1c can see it is not a copy.

## Files considered and rejected

- **`syllabus.pdf` from a platform.** Rejected as an example: it is indistinguishable from the
  coursework fixture and would have added nothing but a second copy of the schema's rule.
- **A `.ics` course reminder.** Rejected: the schema node already carries the calendar fixture,
  and repeating it here would restate the schema rather than research this situation. Calendar
  stays in `file_kinds` nowhere on this row — it is not this situation's evidence.
- **A `.srt` on its own with no sibling media.** Considered and folded into the `.vtt` example
  instead; on its own it is a caption file for anything (a film, a conference talk) and would
  have been a `never_alone` entry masquerading as a file example.
- **A downloaded textbook PDF.** Rejected: it is `research.reading-library` / Reading Inbox
  material and carries no evidence that this situation exists. It informed the
  `falls_through_to: Reading Inbox` entry instead.
- **A `contacts` (`.vcf`) file.** Rejected outright: `00` says contact data "should normally be
  privacy-protected rather than used to create folder proposals", so this situation never sees it.
- **Kept deliberately as the ugly cases:** an unlabelled caption transcript vs. a labelled quiz
  header block (the labelled-form / unlabelled-prose contrast); an OCR'd dashboard (same thing
  seen through a screenshot); a mixed archive; a mail file; two collision fixtures that look like
  this node and belong to neighbours (`PHYS1401 Lecture 08…pptx` → `academic.coursework`,
  `Certified Solutions Architect…pdf` → `career.credentials-licenses`); one file that is also
  another domain (the certificate, which is also career-side; the receipt mail, also finance-side;
  the notebook and the archive, also code-side); and one sparse file (`notes.txt`) that gets
  `group_without_copying_facts: true` and no facts at all.

## `proposed_fields` justification

**None proposed.** Every fact this situation needs is already legal on the Academic schema:
`school` holds the provider (the roster hint's instruction, and `00` itself names "course
provider" as one of the roles an institution name can play), `subject` holds the course,
`work_type` holds the artifact kind, `instructor` stays a search field. Templates add fields only
where no existing key works, and the one place a key genuinely does not exist — the *authoring
university* named beneath a provider on a certificate — is a canonical-field question, not a
template's decision. It is written as `must_not_conclude` on the certificate example and as fork
(1) of `open_question`. Padding it into a private key would be the 574's failure in miniature.

`proposed_context_terms` carries twelve platform-study terms (enrolled, self-paced, module,
lesson, course completion, …). These are **proposals**, explicitly not `00`'s five — the node text
says so where the terms are used, so nobody can later read them as design.

## Neighbours considered that did NOT get an edge

- **`academic` (the schema).** Joined by `schema_id` / `uses_schema`. A `collides_with` to one's
  own schema is a kind violation (`collides_with` joins same-kind pairs only) and meaningless.
- **`research.reading-library`.** A course reading PDF and a library paper genuinely confuse, but
  the confusion is resolved by the *absence* of any signal for this template rather than by a
  discriminating evidence item, so a mutex edge would assert more than is true. The
  `falls_through_to: Reading Inbox` entry carries that case honestly.
- **`code.software-project`.** Rejected in favour of `code.notebooks-experiments`, which is where
  the real one-evidence-item confusion sits (a notebook). A course exercise almost never carries
  the repository markers that make a software project.
- **`college_applications` / `applications.*`.** A completion certificate does turn up inside an
  application packet, but that is a `also_holds_with` shape between **schemas**, and the academic
  schema already carries it. Restating it here would be a template copying its schema's edges.
- **`academic.transcripts-credentials`.** Close on the word "certificate", but that row is
  registrar-issued official records with seals and verification codes tied to a degree; the
  discriminator is the same one already spent on `career.credentials-licenses`, and three
  near-identical collision rows would be noise. Flagged here for R1c rather than authored.
- **`finance.receipts-expenses`.** The order-confirmation example touches it, but the fall-through
  to Receipts and Confirmations already expresses the outcome and the schemas differ in kind of
  evidence, not in a contested evidence item.

## Contract deltas noted (CONNECTION wins)

- **`also_holds_with` is left empty**, against the dispatch prompt's edge table, which offers it
  to any node. `CONNECTION.md` section 5 restricts `also_holds_with` to **schema ↔ schema** only;
  this is a template row, so it may not author one. CONNECTION wins and the prompt says so. The
  two-schema cases are recorded where a template legitimately can record them — the `also_schema`
  slot on four file examples (career, finance, code, photos) — and the schema-level edges remain
  `academic.json`'s to hold.
- **`role_split` is left empty.** `CONNECTION.md` section 6 puts `role_split` in the canonical
  field list, field ↔ field; the one relevant pair (`school` ↔ `target_university`) is already
  recorded on the canonical rows and on the academic schema node. Copying it onto a template is
  exactly the "second copy of the schema's fields" the done-when list forbids.
- **`parent_id` is null and was never authored** (PR-5: R1b never authors browse shelving).
- **`shares_field` is not authored anywhere** (derived-only).
- **`collides_with` reciprocity** is R1c's to complete: this row names four templates, none of
  which has landed a node file yet, so none of them names this row back. That is expected debt,
  not a defect of this node.

## NEEDS-JOSEPH (this node only)

1. **Two institutions, one key.** A completion certificate frequently names *both* a hosting
   platform and an authoring university. This row follows its roster hint and puts the provider in
   `school`, which leaves the authoring university with nowhere to land — it is currently written
   as a thing the extractor must not conclude. Options: (a) accept the loss and keep one
   `school` value per file; (b) add a canonical institution-role key (a `role_split` partner for
   `school`, the same licence `target_university` has); (c) let `school` be multi-valued with a
   role qualifier. This is a canonical-fields decision and no template may take it.
2. **Is this row the same situation as `academic.continuing-education`?** Both are provider-run,
   certificate-terminated, usually termless, and would recommend the same dimensions. The whole
   split rests on whether a professional obligation is present (credit hours, a licensing board, a
   renewal cycle). If Joseph reads that as a **value** distinction — a `work_type` or a provider
   property — then one of the two rows should be withdrawn at R1c, not both padded to justify
   their existence. Recorded as fork (2) of `open_question` rather than silently resolved, because
   resolving it means deleting another agent's node.
