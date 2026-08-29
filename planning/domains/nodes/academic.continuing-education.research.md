# academic.continuing-education — lab notes

Node: `kind: template`, `schema_id: academic`, `launch: placeholder`, `provenance: inference`.
Verdict: **not refused.** Reasoning below.

## Sources used

- `planning/00-database-agent-product-design.md` — read in full; the authority. Every span this
  node puts inside quote marks was grep-verified against this file **before** it was written, and
  re-verified afterwards by walking every string in the emitted JSON and matching each `"…"` run
  against the file (14 quotations, 0 misses). One quotation was corrected in that pass: the
  Homework-3 sentence continues with a comma in `00`, so the closing period was moved outside the
  quote.
- `planning/domains/_CONTRACT.md` — entry shape; rules 8 (snake_case, dimensions must be schema-
  declared), 10 (D1: no career/identity/medical/legal field rows), 11–15 (the R0 delta).
- `planning/domains/CONNECTION.md` — the closed edge vocabulary and the node test. **CONNECTION
  wins over the dispatch prompt** wherever they differ; one such difference is recorded below.
- `planning/prompts/ALIGNMENT.md` — work types are values; a template that only repeats its
  schema's dimension order is not a node.
- `planning/domains/roster.json` — confirmed my id, kind, `schema_id`, and every edge target.
- `planning/domains/canonical_fields.json` — no key was minted. `instructor` is
  `destination_eligible: false` there, which is why it cannot appear in `dimension_order`.
- `planning/domains/nodes/academic.json` — the schema this template points at; its field list,
  work-type values and never-alone list are reused rather than restated.
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — every `source_type` in this node is checked
  against the closed fourteen.
- Not consulted: `planning/deferred-catalogues/`. This node's recognition names two gazetteer
  families (professional providers, accrediting bodies) as **rule families only**; it invents no
  gazetteer contents (R4's) and writes no regex (R2's).

## Why this is a node and not padding

The node test asks whether detection signals, recommended dimensions, or privacy rules differ from
the schema's default template (`academic.coursework`). All three do:

1. **Detection.** Coursework fires on `00`'s pattern-plus-context shape: a course-code-shaped token
   beside one of the five academic context terms. Professional courses characteristically have no
   code-shaped token — the course is titled in prose — so that rule family cannot fire. What fires
   instead is a credit-unit token (CE / CEU / CPE / CLE / contact-hour / PDU shapes) beside a
   completion or course term, plus a provider-approval line. Note this is not a new mechanism:
   `credits` is already one of `00`'s five context terms, and the unit token is what carries the
   professional reading that the bare word does not.
2. **Dimensions.** `term` is dropped, not reordered. `00` validates a term only through dedicated
   academic-term patterns, and material with no semester gives those patterns nothing to match;
   generic date parsing is explicitly forbidden, so a completion date must not become a term. A
   level that nothing can fill is the level `00` tells the canvas to refuse — it would "create
   meaningless one-child levels" or "produce empty branches when tested against the accepted
   group". `school → subject → work_type` is the recommendation.
3. **Privacy.** The defining artifact prints a professional licence or registration number beside
   a legal name. Ordinary coursework does not. Sensitivity is `potentially_sensitive`; the handling
   class is P7's and is not set here.

The difference is therefore not a difference of work types and not a difference of extensions,
which the node test rejects as values and `SOURCE_TYPES` rather than nodes.

## Field reliability, recorded here rather than in `fields`

`fields` is `[]` by design — a template references its schema and never copies the field list
(_CONTRACT rule 12, CONNECTION §3.1). But the ceilings the **schema** records do not all hold in
this situation, and that is a finding worth carrying to R1c:

| Field | Schema's ceiling | Here | Why the difference |
|---|---|---|---|
| `school` | `validated` | `possible` (→ `validated` only with a provider gazetteer) | The rule family that validates `school` is a **schools** gazetteer hit. A trade body, a training company or an employer learning portal is not in one. `00` names the ambiguity directly and lists *course provider* as one of the six roles a bare institution name can play, so the name alone cannot even establish the provider reading. |
| `subject` | `validated` | `llm_supported` (→ `direct` from a labelled Course cell) | `00`'s validating rule is a **code pattern** plus context. A prose course title matches no code pattern. A labelled table cell is direct — `00`'s table sentence is why the extractor keeps cell provenance. |
| `term` | `validated` | `possible`, usually absent | Academic-term patterns do not match completion dates or renewal periods, and fuzzy date parsing is forbidden. |
| `work_type` | `validated` | `validated`, unchanged | The one fact a sparse handout here can carry alone. |
| `instructor` | `direct` from a labelled slot | unchanged | Never a folder level (canonical row, and `00` on authorship as a destination). |

No field was proposed. `proposed_fields` is `[]`.

## proposed_fields justification — why the list is empty

Two candidates were considered and both were rejected rather than minted:

- **A credit-hours count** (`ce_credit_hours` or similar). Rejected: the count is *evidence*
  supporting `work_type = completion certificate` and a search attribute at most. Minting a
  per-domain numeric field is exactly the 574's failure — 2,295 names for one vocabulary — and it
  would also put a number into a catalogue that holds none.
- **The credential the credits are earned toward** (CPA, RN, PMP, bar). This is the dimension a
  professional actually browses by, and no canonical key holds it. It was **not** proposed because
  it is a career-domain field, and career field rows are deferred (_CONTRACT rule 10, D1 as
  narrowed; PR-6). Proposing it here would be reversing S3 as a side effect of one template row.
  It is filed in `open_question` instead, and it is the substantive NEEDS-JOSEPH below.

## Files considered and rejected

Kept twelve examples, including four that are *not* this template — the collision fixtures earn
their place because they are what the never-alone rules have to survive.

Rejected from the list:

- **A .vcf for a course instructor.** `00` says contact data "should normally be privacy-protected
  rather than used to create folder proposals"; it would add a `SOURCE_TYPE` row and no signal.
- **A generic `.mp4` lecture recording with no metadata.** It duplicates `Module 4.pdf` as a sparse
  file and adds nothing beyond `audio_video`, which is already in `file_kinds`.
- **A password-protected certificate archive.** It is entirely `Unsupported or Encrypted`'s story
  (R3's), not this template's; the archive case is already carried by `CE_2025_bundle.zip`.
- **A LinkedIn-style course-completion post screenshot.** Its academic content is nil; it would
  have taught only that a screenshot with no credit statement stays a screenshot, which the
  existing OCR example already teaches with a real credit statement.

The sparse-file rule shows up twice: `Module 4.pdf` and `CE_2025_bundle.zip` both carry
`group_without_copying_facts: true`. Neither takes a course title from a neighbouring certificate —
`00`: "The graph does not automatically copy those missing facts onto sparse files." Activation is
not grouping: a handout with no provider and no credit token may join a P9 course neighbourhood and
still activate nothing from its own filename.

## Neighbours considered that got no edge, and why

- **`career` (the schema).** It is on my `must_consider_neighbors`, and it gets **no edge from this
  row**. CONNECTION §5 closes the vocabulary: `collides_with` joins **same-kind** pairs, and
  `also_holds_with` joins **schemas only**. A `kind: template` row therefore cannot legally point
  either edge at a schema. Where the prompt's edge table reads as though a template may author
  `also_holds_with`, **CONNECTION wins and this node authored none** — `also_holds_with: []`. The
  real relationship is already asserted one level up: `academic.json` carries
  `also_holds_with: career` for exactly this material ("a transcript, course-completion certificate
  or professional-certification record"). The file-level fact is still recorded where it belongs —
  the employer-training certificate example carries `also_schema: "career"`, which is an observation
  about that file, not an authored edge.
- **`career.credentials-licenses` (template).** Got a `collides_with`. This is the sharpest
  confusion in the whole node: a completion certificate and a licence certificate are the same
  shape of PDF naming the same person and the same profession. The discriminator is a *course of
  study plus a credit statement* versus *the licence itself with an issue or expiry date*. The
  renewal-notice fixture is the false file that proves the rule.
- **`academic.online-course` (template).** Got a `collides_with`. A MOOC certificate and a CE
  certificate are near-identical; the discriminator is an accrediting body and a credit unit. The
  Coursera fixture is the collision file.
- **`academic.coursework`** and **`academic.transcripts-credentials`** — both got `collides_with`,
  reasons on the edges. The `NURS 3100` syllabus is the coursework fixture: nursing subject matter
  and the word *credits* both point this way, and the term pattern plus the degree-granting
  institution decide it the other way.
- **`academic.standardized-testing`.** Considered, no edge. Its evidence is a test name and a score
  report; nothing in this node's signal set can be confused with it.
- **`finance` / `career.employment-records`.** Considered for the tuition-reimbursement and
  employer-sponsorship cases. No edge: the *receipt* fixture falls through to Receipts and
  Confirmations by `falls_through_to`, which is the mechanism `00` already provides, and inventing a
  finance collision from a payee name would be the bare-institution-name error.
- **Residual `Independent Records`** is reached by `falls_through_to`, which is required rather than
  optional here — `00` gives standalone certificates to that home by name, so the residual would
  shadow this template if the edge were missing (CONNECTION §5 invariant 5).

## Reciprocity debt for R1c

`academic.online-course` **already reciprocates** — its node landed while this one was being
written and independently names `academic.continuing-education` as its closest neighbour, with the
same discriminator (a certificate PDF is one evidence item that supports both) and, arrived at
independently, the same `school → subject → work_type` dimension order. That agreement is a useful
cross-check on the term-dropping decision.

The remaining three edges are one-way from this row, and R1c must add the reciprocals on
`career.credentials-licenses`, `academic.coursework` and `academic.transcripts-credentials`. Each
carries a non-empty `signal` already. Note that `academic.coursework` as landed lists seven
collisions and this row is not among them, so that reciprocal is a genuine gap rather than a
wording mismatch.

## NEEDS-JOSEPH (this node only)

1. **The credential has no field, so the level professionals browse by cannot be recommended.**
   CE is organized in real life by the credential the hours count toward — CPA, RN, PMP, bar — and
   that is a career-domain field, deferred under D1/PR-6. Until career fields land, this template
   can recommend only `school → subject → work_type`, and its second grouping reason (one
   credential's reporting period across several providers) has no field to hang on. Two ways out,
   both Joseph's: add one credential field to the canonical list early (which is reversing S3 for a
   template row, and must be decided as such), or accept that CE files group by provider and course
   until P10 needs the career schema anyway.
2. **May `term` hold a reporting or renewal period as a VALUE?** A 2025 reporting period or a
   two-year renewal cycle would restore a fourth level and would match how compliance material is
   actually filed. Against it: `term`'s validating rule family is explicitly the academic-term
   pattern, so a period-shaped number would reach the field through no rule, and `00` is emphatic
   that year-shaped numbers are the classic false positive. This node assumed **no** and dropped
   the level. If Joseph reverses it, the change is `dimension_order` here plus a term-pattern
   family in R6, not a new field.
