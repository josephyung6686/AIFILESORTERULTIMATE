# academic — R1b lab notes

Row: `kind: schema`, `domain_id: academic`, `launch: full`, `parent_id: null`.
Node test: **passed** — 00 names this schema and its five fields outright, and no other roster
schema is a respelling of it. `refuse_node: false`.

## Sources used

- `planning/00-database-agent-product-design.md` — read in full; the authority. Every quoted span
  in `academic.json` was grep-matched against this file before it was written (script check:
  0 unverified spans).
- `planning/01-product-design-structured.md` — §3.2 (observations vs facts), §3.5/§3.6 (how facts
  are produced and validated), §3.11 (domain-scoped schemas), §3.13 (reliability states),
  §5.4–§5.6 (templates, the Academics worked example, purpose-defined packets). Used as a locator
  only; 00 wins and every quotation is taken from 00's own wording.
- `planning/domains/_CONTRACT.md` (entry shape, D6 = `subject`, rules 5/8/14),
  `planning/domains/CONNECTION.md` (closed edge vocabulary, activation algorithm shape, node test,
  PR-1 and PR-7), `planning/domains/CONNECTION-EXAMPLES.md` (fixtures 1, 3, 5, 6, 7),
  `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — confirmed the row, its ten sibling schemas, and the twelve
  `academic`-schema templates that will be researched separately.
- `planning/domains/canonical_fields.json` — all five field keys resolve; nothing minted.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` (all twelve file examples check out).
- No `planning/deferred-catalogues/` file was consumed: the two rule families this node names
  (schools gazetteer, academic term patterns) are R4's and R6's content, and this node names the
  family without writing a regex, a gazetteer entry, or a threshold.
- Neighbour node files: none had landed when this was written (`planning/domains/nodes/` held only
  `.gitkeep`), so the edges below are authored one-way and R1c owes the reciprocals.

## Files considered and rejected

Kept twelve examples (eight were the floor). Rejected as examples, with the reason:

- **A professor's `.eml` course announcement.** Realistic, and `email` is a `SOURCE_TYPE`, but the
  activation would ride entirely on the message body's course evidence — the example would repeat
  the `.ics` fixture's lesson (content decides, the format never does) without adding a new
  failure mode. `email` is therefore absent from `file_kinds.source_types`; a template that
  genuinely lives on mail (the K-12 or teaching rows) may add it.
- **`Textbook_Chapter_4.pdf` (a scanned course reading).** It is Reading Inbox's case, not an
  academic-fact case: a chapter scan carries no course code, no term and no school, and treating
  a course-adjacent reading as coursework is exactly the over-reach `falls_through_to: Reading
  Inbox` exists to absorb.
- **`node_modules/…` and a `package.json`-rooted homework repo.** 00 excludes software project
  descendants from the proposal engine before extraction; a code-project file that happens to be a
  class assignment is the `code` schema's, and the academic facts (if any) come from the README,
  not from the tree.
- **A student ID card scan.** Reads academic, behaves as identity: safety domain, Protected
  Records. Including it would have invited a `falls_through_to: Protected Records` on this row and
  turned an ordinary domain into a safety one.
- **`Tuition_Invoice_Fall2025.pdf`.** Carries a school name and a term-shaped token, and is a
  finance record (`institution`, `record_type`). Left out because the collision it demonstrates is
  finance's to state; noted here so R1c can decide whether `academic ↔ finance` deserves a
  reciprocal `collides_with` (my read: the discriminating evidence is billing language versus
  course-plus-context, and the edge is worth having — but I did not author it, see below).

## Fields — why exactly the five, and no sixth

`proposed_fields: []`. The five inherited keys are 00's own Academic sentence and they already
split into four destination-eligible dimensions plus one search/review field (`instructor`), which
is the shape 00 describes: "usually three to six that may help build a future folder proposal and
several additional fields used only for search, privacy protection, explanation, or later review."

Fields I considered and did **not** propose:

- `grade` / `score`. Tempting for transcripts and gradebooks, but it is a value-bearing detail with
  no folder role, high sensitivity, and no 00 sentence. If any template needs it, it needs it as a
  search field and should argue for it there.
- `assignment_number` (the `3` in `HW 3`). This is a value inside the `work_type` neighbourhood and
  a version/duplicate concern, not a new column. Minting it would re-create the 574's per-detail
  field habit.
- `program` / `degree` / `major`. Real for a transcripts or study-abroad template; as a schema
  field it would be a fifth destination dimension that 00's template order does not use, and
  `subject` already holds the study-subject role.
- `institution`. Already canonical, and using it here beside `school` would be two columns for one
  concept — the exact D6 defect. Academic uses `school`.
- `purpose`. Blocked by PR-1: it stays a College-applications field. A purpose-coherent academic
  packet activates the nearest schema on its own evidence or falls through to residual.
- A `document_type` beside `work_type`. `application_document_type` exists for the applications
  side; duplicating it here would be a synonym.

One non-obvious call: **`instructor` has ceiling `direct`, not `validated`.** `validated` would be
a claim that a rule family confirms it later, and there is none — no person gazetteer is in scope.
What is true is that a labelled table cell or form slot reaches `direct` under P4's D11, and prose
or OCR stays `possible`. Setting `validated` would have been the kind of unearned promise the
contract's rule 4 exists to catch.

## Recognition — what the fact-check changed

- The deterministic list is written against the twelve files above, not against slogans. Each entry
  fires on at least one of them and would not fire on `Resume_2026.pdf` or `Columbia Essay.docx`.
- **`proposed_context_terms` is a proposal, and one candidate was deliberately excluded.**
  "coursework" and bare "course" look like obvious additions to 00's five (syllabus, lecture,
  credits, instructor, semester) and are the single most dangerous ones: `Relevant coursework:
  BUSIB 4300` on a resume would then satisfy pattern-plus-context and write a false `subject`.
  The twelve proposed terms are all document-describing (grading policy, office hours, prerequisite,
  registrar …) rather than list-introducing. R2/R6 own the actual detectors; this is a candidate
  list with a warning attached, not a regex.
- **Activation ≠ grouping is encoded twice**: `HW 3.pdf` and `IMG_5512.HEIC` both carry
  `group_without_copying_facts: true`, and `submission.zip` carries it because its manifest may
  pull members into one packet without giving the archive their facts.
- **Positional weight is doing real work** in two `must_not_conclude` lines (resume enumeration,
  reference-list venue). 00 supplies the rule; no number appears.

## proposed_fields justification

None proposed. If a later template on this schema (transcripts-credentials, standardized-testing,
k12-schooling) finds it cannot express its situation with these five keys, that is its own
`proposed_fields` argument to make with its own file evidence — not a pre-emptive widening here.

## Neighbours considered that did not get an edge

- **`code`.** A programming course produces a repo. But the confusion is resolved structurally
  (repo markers, package manifests) before any academic signal is weighed, and 00 tells the engine
  to preserve existing project layout rather than scatter it. Neither a collision nor an
  also-holds; a course-project repo is a `code` file whose README may carry academic facts, which
  is already covered by co-activation on disjoint evidence generally.
- **`finance`.** Tuition invoices, financial-aid letters and student-loan statements sit right on
  the seam (school name + term-shaped token). I judged this a real `collides_with` but did not
  author it: finance is a safety schema, its side of the edge changes what P7 does first, and
  writing a one-way edge into a safety row from an ordinary row is a decision R1c should take with
  the finance node in front of it. **Recorded here as an R1c candidate.**
- **`identity`.** Student ID cards and visa-bearing study-abroad paperwork. Left to the
  `academic.study-abroad` template, whose privacy rules differ; the schema row should not acquire
  a safety edge on the strength of one artifact.
- **`medical`.** Only reachable through `academic.iep-accommodation-plans`, which is a placeholder
  template with its own privacy story. Not a schema-level edge.
- **`photos` did get an `also_holds_with`** even though the roster's `must_consider_neighbors` did
  not name it. Justification: the CONNECTION fixtures already activate `photos` on camera EXIF, 00
  names the photographed homework page, and the two schemas then hold on genuinely disjoint
  evidence (EXIF versus OCR). That is the textbook shape of `also_holds_with`, and it is the edge
  that keeps a photographed worksheet from being forced to choose.
- **`career` carries both edges.** The collision is the resume case: a resume is not partly
  coursework, it is a different document that mentions a school, so the edge asserts a
  discrimination rule. The also-holds is narrower and was added late, after the `career` node
  landed mid-session and authored the same pair toward `academic`: a transcript or certification
  record is an academic artifact serving a recruiting process, on disjoint evidence. Career is a
  field-less placeholder schema (PR-6), so co-activation is asserted, not a field overlap.

**Reciprocity and mid-session neighbours.** `college_applications`, `career`, `photos` and `code`
node files landed while this one was being written; they were read, not rewritten. Alignment
found: `college_applications` states the mirror of both this node's edges and the same
`school ↔ target_university` role split (its shape uses a `neighbor` key, which this node adopted
so the pair merges without a rename). `career` states the mirror of both of its edges. `photos`
authored no academic edge, so the `also_holds_with` toward it is one-way and R1c owes the mirror —
its justification is above and in the `IMG_5512.HEIC` example. `research` had not landed. Per the
contract, the `research`, `college_applications` and `career` pairs each carry both edges, so each
`collides_with` side keeps a non-empty discriminating `signal`.

## Template note (the one honest tension)

`dimension_order` is 00's own `school → term → subject → work_type`. 00 also says, of document and
record domains generally, that "project, function, or subject usually comes before time", which
would argue `subject → term`. Both sentences are 00's, and 00 resolves the tension itself by
showing the alternative as a user choice (its Option B is course → term → work type). So the node
recommends 00's stated Academic order and records that the user may reverse or flatten it; no
invented compromise order was written. `time_first: false`.

`instructor` is excluded from `dimension_order` because it is not destination-eligible — a
person-named folder is exactly the collector 00 warns against.

## Deviations and precedence

None. CONNECTION.md and the dispatch prompt did not conflict on anything this node needed: the
edge vocabulary used here (`collides_with`, `also_holds_with`, `falls_through_to`, `role_split`,
`file_kinds`) is the closed list, `parent_id` stays null and unauthored, `shares_field` is not
serialized, and no handling class, threshold or folder path appears anywhere in the JSON.
One key beyond the prompt's skeleton was added — `proposed_context_terms` — because the prompt
explicitly invites it; `check.py` globs only `planning/domains/*.json`, so this file is not scanned
as a catalogue entry and the extra key costs nothing.

## NEEDS-JOSEPH (this node only)

- **NJ-academic-1 · Domain-wide sensitivity, or work-type-scoped?** Recorded as the node's
  `open_question`. 00 counts "educational records" inside the highly personal corpus, but most
  coursework is a lecture deck. If the whole domain is `potentially_sensitive`, ordinary coursework
  never reaches a cloud dossier; if only grade-bearing and roster-bearing work types are, then a
  privacy boundary depends on a `validated` fact that can be absent. Not resolvable from 00.
- **NJ-academic-2 · Whose school is `school` when the holder is not the student?** K-12 records,
  homeschooling portfolios and teaching-side gradebooks are held by a parent or an instructor, and
  the school on the file is the child's or the employer's. 00's role-split machinery exists for
  exactly this shape but names no academic role pair. Flagged, not solved: inventing a
  `child_school` key here would be the 574's move. It belongs to the k12/teaching templates plus a
  canonical-field decision.
- **NJ-academic-3 · A transcript's `subject` and `term` are inherently multi-valued.** One file,
  many course rows. The node refuses a single value (see the `Official_Transcript_2026.pdf`
  example) and P6's `file_facts` shape allows many rows per file, but whether a multi-valued
  `subject` may drive a folder dimension (one file, many course branches) is a P10 question with a
  shared-material policy attached.
