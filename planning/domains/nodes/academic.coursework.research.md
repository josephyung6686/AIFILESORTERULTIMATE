# academic.coursework — lab notes

Row: `kind: template`, `schema_id: academic`, `launch: full`, `refuse_node: false`.
Output: [`academic.coursework.json`](academic.coursework.json).

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every span this node puts inside
  quote marks was grep-matched against this file before it was written; a verification pass over
  the finished JSON extracted all 34 quoted spans and confirmed each appears verbatim. One span
  failed that pass on the first run (a bracketed `appear[s] … ha[s]` edit of the Reading Inbox
  sentence) and was replaced with the literal substring. No quote in the node is paraphrased.
- `planning/01-product-design-structured.md` — §§5.4–5.9 only (templates as controlled schemas,
  the worked Academics options, purpose-defined packets, the template library sentence, uneven
  depth, the scoped `General`). Used as a locator; every claim was re-read in `00`.
- `planning/domains/_CONTRACT.md` (all), `planning/prompts/ALIGNMENT.md` (all),
  `planning/domains/CONNECTION.md` (all), `planning/domains/CONNECTION-EXAMPLES.md` (all).
- `planning/domains/roster.json` — confirmed the row, its `schema_id`, and every id used on an
  edge. `planning/domains/canonical_fields.json` — every field key referenced resolves to it.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked mechanically against all fourteen
  file examples.
- Landed neighbours: `nodes/academic.json` (the schema), `nodes/college_applications.json`,
  `nodes/research.json` — read to align, not rewritten.

## The node test — why this row was not refused

This is the one row where refusal was genuinely on the table, because the roster's own hint calls
it "The Academic schema's default situation" and its `dimension_order` is the schema's. The prompt
refuses a template whose detection signals, dimension order **and** privacy rules are all identical
to the schema's default. Three findings decided it:

1. **`CONNECTION-EXAMPLES.md` is binding and names this row twice.** Fixture 1 emits
   `{"edge": "uses_schema", "from": "tpl.academic-coursework", "to": "academic"}` with the
   school → term → subject → work_type recommendation; fixture 7 names it as the *taking a course*
   situation beside `tpl.academic-teaching`. That file states R1 output "must remain compatible
   with every one of them" and that a roster on which any example "becomes inexpressible … is
   wrong." Refusing this node makes both fixtures inexpressible.
2. **The detection signals are strictly narrower than the schema's.** The Academic schema must
   also admit transcripts and registrar records, standardized tests, MOOC/platform material, K-12
   records and the teaching side — eleven sibling templates hang off it. This template's signals
   require *enrolment-side, single-holder, one-course-one-term* evidence and explicitly route the
   roster/gradebook shape away.
3. **The privacy rule differs, and differs in a direction, not a degree.** Both this row and the
   schema are `potentially_sensitive`, but the rule authored here is that this situation holds the
   holder's **own** record and must not accumulate other people's — a roster column or a scores
   table is `academic.teaching`'s signature and is a routing signal *away* from this template.
   That is a distinct privacy rule, which is the third leg of the test.

`work_types[]` was also narrowed on purpose (no `gradebook`, no `transcript`, no `diploma`) — those
are values that belong to the teaching-side and official-record situations.

**Recorded honestly:** the schema row `academic.json` already carries an inline `template` block
with the identical `dimension_order`. Two rows now state one recommendation. That duplication is
real and I did not resolve it unilaterally; it is this node's `open_question` for R1c/Joseph.

## Where CONNECTION overrides the dispatch prompt

The prompt offers `also_holds_with` in the edge table. `CONNECTION.md` §5 restricts
`also_holds_with` to **schema ↔ schema only**, and §5's `collides_with` row restricts collisions to
**same-kind pairs**. On conflict CONNECTION wins, so:

- `also_holds_with` is **empty** on this template row. The academic ↔ college_applications,
  academic ↔ research and academic ↔ photos co-holding facts are true of my file examples
  (`submission.zip`, `Senior Thesis Draft 3 - BIO 4990.docx`, `IMG_5512.HEIC`) and are already
  authored on `nodes/academic.json`, where the edge is legal. They are recorded here through
  `file_examples[].also_schema` instead, which is a fixture annotation and not an edge.
- `collides_with` names **template ids only** — verified against the roster, all seven targets are
  `kind: template`. `must_consider_neighbors` gave me the schema ids `college_applications` and
  `research`; I resolved each to its full-launch template (`applications.undergraduate-packet`,
  `research.project-workspace`) rather than authoring a cross-kind edge.
- Reciprocity is R1c's, per the prompt.
- `parent_id` is `null` and was never authored (PR-5: R1b never authors it).
- `shares_field` is nowhere in the file.

## Files considered and rejected

- **`Transcript.pdf` / `Official_Transcript_2026.pdf`** — rejected as a *this-node* example. It is
  the `academic.transcripts-credentials` situation: registrar language plus a table of many
  course-term rows, so no single `subject` or `term` value describes the file. It survives here
  only as a `collides_with` seam and as a member inside `submission.zip`.
- **`Course Notes.md`, `notes.txt`** — rejected: a bare notes file with no course token, no term
  and no context term adds nothing the `HW 3.pdf` and `problem set 4` fixtures do not already
  cover, and `CONNECTION-EXAMPLES` fixture 3 already owns the "one entity name in the body"
  refusal.
- **`Diploma.pdf`, `SAT Score Report.pdf`** — rejected: sibling templates
  (`academic.transcripts-credentials`, `academic.standardized-testing`) own these situations.
  Naming them here would be the label-grab this pass exists to prevent.
- **A `.vcf` of a study group** — rejected: `00` says VCF data "should normally be
  privacy-protected rather than used to create folder proposals", so it can never be a coursework
  fixture. `contacts` is deliberately absent from `file_kinds.source_types`.
- **`node_modules`-style code drops inside a course folder** — rejected: `00`'s exclusion rules
  strike these before the domain layer ever sees them.
- **A lecture recording (`.mp4`)** — considered, left out of `file_kinds`. `audio_video` extraction
  is gated behind `00`'s explicit privacy-and-compute policy for transcripts; asserting it as a
  plausible coursework kind would over-claim what the extractor tier delivers at launch. Worth
  revisiting once P5's audio_video tier is settled — not a NEEDS-JOSEPH, an R1c note.

## `proposed_fields`

**None.** The five inherited keys (`school`, `term`, `subject`, `instructor`, `work_type`) covered
every fact in all fourteen file examples. Two near-misses were deliberately *not* minted:

- A "course section" or "meeting time" key (from the registration confirmation and the `.ics`) —
  that is a **value** detail, not an organization dimension, and `00` says the system "should not
  invent new fields automatically."
- A teaching-side authorship key (the `instructor` on a coursework file is someone else; on a
  teaching file it is the holder). If that ever needs a field, `CONNECTION-EXAMPLES` fixture 7 says
  the answer is a `role_split` between canonical keys or a second template — never a new field
  minted by a template row. Flagged for R1c, not authored.

`proposed_context_terms` extends `00`'s five (`syllabus`, `lecture`, `credits`, `instructor`,
`semester`) with thirteen coursework-register terms. They are proposals; the node never claims `00`
listed them, and no regex is written here (that is R2's).

## Neighbours considered that got no edge

- **`academic.k12-schooling`, `academic.homeschool`, `academic.study-abroad`,
  `academic.continuing-education`, `academic.iep-accommodation-plans`,
  `academic.recommendation-letters-written`** — all siblings on the same schema, but none of them
  is confusable with this row *on one evidence item*. K-12 and homeschool differ by who holds the
  file; study-abroad is this situation with two `school` values, which is a value question;
  continuing-education differs by provider register. `collides_with` means evidence-item mutex, not
  "adjacent topic", and padding the list would recreate the 574's misuse of the edge.
- **`photos.screenshot-captures` / `photos.scanned-documents`** — the course-site screenshot and
  the photographed problem sheet touch both, but the discrimination is a `SOURCE_TYPE` plus EXIF
  question that `00` already settles ("the system must not mistake the absence of EXIF for proof
  that an image is a screenshot"), and the co-holding is a schema-level fact. Handled through
  `also_schema` and `falls_through_to` (Temporary Screenshots, One-Off Images) instead.
- **`finance.student-financial-aid`** — a tuition invoice sits near coursework, but its evidence is
  financial-institution and amount shaped; no single evidence item makes it confusable with a
  syllabus. No edge.
- **`code.software-project`** — a course programming assignment was considered. The repository
  markers `00` names (`package.json`, `requirements.txt`) are decisive and structural, so the pair
  does not contend over one item. Left to `academic` ↔ `code` at schema level if anyone wants it.

## NEEDS-JOSEPH (this node only)

- **NJ-coursework-1 · Who owns the Academic default template?** `nodes/academic.json` carries an
  inline `template` block identical to this row's `dimension_order`, and `CONNECTION.md` §8's
  `destination_dimensions(domain_id)` allows a schema id "resolving through the schema's default
  template". Either the schema row's block is redundant with this row, or a schema keeps its own
  default and this row is the *taking a course* specialisation of it. Both readings are live; the
  node states the recommendation because the fixtures require the row to exist. This is the node's
  `open_question`.

Two questions were considered and **not** filed, because they are already open elsewhere and
duplicating them would inflate the count: whether `potentially_sensitive` attaches to the whole
Academic domain or only to its grade-bearing work types (already `academic.json`'s open question),
and the counting rule for "500+" (NJ-1 in `CONNECTION.md`).
