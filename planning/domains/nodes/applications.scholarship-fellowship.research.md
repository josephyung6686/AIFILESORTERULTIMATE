# applications.scholarship-fellowship — R1b lab notes

Roster row: `kind: template`, `schema_id: college_applications`, `launch: placeholder`,
`provenance: proposal`. Verdict: **node stands** (`refuse_node: false`). No field minted.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node
  JSON was grep-matched against this file **before** it was written; the final file carries
  48 quoted spans and all 48 match verbatim. Two mechanical passes were run (one naive, one with
  possessive apostrophes masked) and the only "miss" was a regex artifact from the word `OCR'd`,
  which was rewritten to `OCR-derived` so the file greps clean.
- `planning/domains/_CONTRACT.md` — entry shape, rules 5, 6, 8, 10, 11–15.
- `planning/domains/CONNECTION.md` — sections 2 (node test), 3, 5 (closed edge vocabulary),
  6 (field identity), 7.
- `planning/domains/CONNECTION-EXAMPLES.md` — fixtures 2 (two schemas at once), 3 (name alone),
  6 (`HW 3.pdf`), 8 (one vocabulary, three templates: the direct precedent for this row).
- `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — id, kind, schema, neighbours confirmed; collision partners
  chosen from the live template list.
- `planning/domains/canonical_fields.json` — every field key referenced resolves here.
- `planning/domains/nodes/college_applications.json` — the schema this template points at,
  already landed. Aligned to, not rewritten.
- `planning/domains/ROSTER.md` — NJ-R1a-6, the recorded sponsor/`target_university` tension.
- `planning/01-product-design-structured.md` — **not** read beyond confirming it is the numbered
  rendering. `00` was read in full and is the authority; nothing in this node needed a locator.
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — taken from the dispatch prompt's verbatim
  list and machine-checked against every `file_examples.source_type`.

## The node test, worked honestly

The refuse condition for a template is: detection signals, dimension order, **and** privacy rules
all identical to the schema's default template. I checked all three separately rather than
assuming a difference.

1. **Detection signals — differ decisively.** The schema's leading deterministic rule is a
   schools-gazetteer hit plus admissions-role context. Most sponsors in this situation are
   foundations, civic clubs, professional societies, employers and government programs, which no
   schools gazetteer contains. That rule mostly *misses* here, and the situation is carried
   instead by award-and-eligibility language. This is not a rewording of the schema's rule; it is
   a different primary anchor.
2. **Privacy rules — differ.** Financial-need documentation is constitutive of a need-based
   scholarship packet, not incidental to it. `00` orders a tax statement or an account record into
   immediate protection, which means this branch's ordinary working set contains protected
   material by design. The undergraduate packet's privacy load is an identification document; this
   one's is a tax record, and the co-activating neighbour differs accordingly.
3. **Dimension order — differs, flagged rather than asserted.** See below.

Two of three would have been enough. I did not need to manufacture the third, and I did not treat
it as free.

## The dimension-order call, and why it is an `open_question` rather than a finding

Recommended: `application_cycle → application_document_type → target_university`. The schema's
default is institution-first.

The argument for reversing: one applicant addresses many sponsors in one season, most receiving a
single essay and a single form. Institution-first lands squarely on the canvas warning `00`
writes into the product — a level that "creates a large number of tiny folders" and a dimension
that does not "materially improve retrieval". Cycle-first keeps the reusable essay family and the
shared supporting set where the applicant looks for them, and leaves the sponsor as the deepest
split so it only opens where a sponsor produced a real packet.

The argument against, which I did **not** suppress: `00` states that for document and record
domains "project, function, or subject usually comes before time", and names capture media as the
exception — not this. I set `time_first: true` deliberately so the departure is visible to R1c
rather than buried in the `why` prose, and added a `time_first_note` saying it is not a claim of
`00`'s photo exception. The fork is written into `open_question`, and the resolution `00` itself
prescribes is the canvas: "The user sees the actual branch counts before committing."

I considered `application_document_type` first (essays / forms / supporting / outcomes at the top,
cycle beneath). It reads well and avoids the time-first departure, but it splits one sponsor's
packet across three top-level branches, which breaks exactly the purpose-coherence this domain
exists to preserve. Rejected on that ground.

## proposed_fields — deliberately empty

The obvious temptation is a `sponsor` or `awarding_organization` key beside `target_university`,
because the target here is usually not a university. I did not mint it:

- ROSTER.md NJ-R1a-6 already records the fork against this exact row and says the row "ships
  against the existing key until Joseph answers".
- The canonical list already holds four organization-shaped keys (`institution`, `lab`, `venue`,
  `client`) whose role sentences do not fit an application addressee. A fifth would be a private
  synonym, which is the 574's defining failure.
- Nothing in the node depends on the answer. The recognition rules, the collisions, and the
  dimension order are all identical under all three of NJ-R1a-6's options; only the key's spelling
  changes. That is the test I applied before deciding not to mint.

Recorded instead in `open_question` and in `proposed_fields_note`.

## Files considered and rejected

- **`Tuition Invoice - Fall 2026.pdf`** — carries the word scholarship in a credit line. Rejected
  as a fixture in favour of `FAFSA Student Aid Report 2026.pdf`, which is the same collision but
  sharper: it is the file most likely to be mis-activated here and it belongs to
  `finance.student-financial-aid`. Kept only as the reasoning behind the `never_alone` entry for
  the bare word *scholarship*.
- **`Letter of Recommendation - Prof Alvarez.pdf`** — a recommender-authored file. Dropped
  because the interesting facts on it are the recommender's identity, and `00` forbids authorship
  as a destination dimension; it adds nothing this node's other fixtures do not already show, and
  `academic.recommendation-letters-written` is the roster row that actually holds that situation.
- **`Study Abroad Scholarship - Learning Agreement.pdf`** — genuinely dual with
  `academic.study-abroad`, whose node already landed and already claims the learning-agreement
  shape. Dropped rather than fight a landed neighbour over a fixture; the collision is thin
  (the discriminator is obvious: an agreement about credit versus an application for money).
- **`W-2 2025.pdf`** — the finance-side need document. Superseded by
  `Tax Return 2025 - Parent Copy.pdf`, which makes the same point and additionally exercises the
  "folder context is a clue, not a fact" rule because it sits inside an award-named folder.
- **A boarding pass / travel confirmation for an award ceremony** — real, but it evidences
  `Receipts and Confirmations` and nothing about this node. Excluded rather than pad the residual
  list.

14 fixtures shipped, covering `text_document`, `spreadsheet`, `image`, `archive`, `email`,
`calendar`; labelled form vs unlabelled prose; a portal screenshot; a manifest-only archive; two
collision fixtures that look like this node and are not; three that legitimately carry a second
schema; and one sparse file.

## The `HW 3.pdf` shape, for this domain

`Essay.docx` is it: a bare document-role filename, a body with no award, no sponsor, no deadline
and no prompt, sitting beside three sponsor-named siblings. It is marked
`group_without_copying_facts: true` and its `facts_legal` is empty. Four fixtures carry that flag
in total — `Essay.docx`, `Official Transcript.pdf`, `Tax Return 2025 - Parent Copy.pdf`, and
`scholarship_packet.zip` — because the shared-supporting-document and manifest cases are the same
firewall from the other direction: a packet may contain a file whose own bytes evidence none of
the packet's facts.

## Neighbours considered that got **no** edge, and why

- **`academic` / `finance` / `research` (the roster's `must_consider_neighbors`)** — all three are
  `kind: schema` rows. `collides_with` joins same-kind pairs only (CONNECTION §5), so a template
  cannot collide with a schema. I resolved each to its template-level counterpart instead:
  `finance` → `finance.student-financial-aid`, `research` → `research.grants-funding`,
  and `academic` → **no edge**, because the academic confusion here (an essay that describes the
  writer's own school) is a *field-role* problem, not an evidence-item mutex — so it is written as
  `role_split` pointing at `academic` rather than as a collision. Noted here because the dispatch
  prompt says to prefer `must_consider_neighbors` and I departed from two of the three.
- **`career.recruiting`** — a fellowship statement and a cover letter share a shape, and some
  fellowships are employer-sponsored. Not authored: the schema row already carries
  `college_applications ↔ career` as a collision with the addressee discriminator, and repeating
  it one level down adds no discriminating signal a template could act on. Left to R1c.
- **`applications.purpose-packet`** — the closest sibling, since a scholarship packet *is*
  purpose-coherent. Not a collision: that template's business is the flat purpose-defined packet
  as an organizational choice ("a purpose-defined packet, such as Chinese University Application
  Materials"), and a file being purpose-coherent is not an evidence item that could be
  mis-attributed between the two. They are alternative shapes for overlapping material, which the
  closed vocabulary has no edge for — and inventing one is a gate failure.
- **`academic.transcripts-credentials`** — the transcript copy fixture overlaps it. Not authored
  as a collision because the discriminator is not in dispute (an issuer-and-attestation document
  versus an application addressed to a sponsor) and the landed node already claims that shape.
  The overlap is represented as `also_schema: "academic"` on the fixture, where it belongs.
- **`identity.core-documents`** — an ID copy inside the packet. Not a collision; the schema row
  already carries `college_applications ↔ identity` as `also_holds_with`, and safety activation
  unlocks protection plus a field-less schema, never a competing template.

## For R1c

- **A schema-level pair this node's evidence supports and the schema does not yet assert:**
  `college_applications ↔ finance` as `also_holds_with`, on disjoint evidence — an award letter
  that also instructs a disbursement, and a need-documentation member that is a financial record
  in its own right. A template may not author `also_holds_with` (schemas only), so it is recorded
  here and in `also_holds_with_note` rather than written. It is a recommendation, not a finding:
  the finance schema is a safety row and the pair has protection consequences that are not mine
  to decide.
- **Reciprocity owed:** four `collides_with` edges are authored one-way from this node —
  `finance.student-financial-aid`, `research.grants-funding`,
  `applications.undergraduate-packet`, `applications.graduate-professional`. None of those four
  node files existed when this one was written.
- `parent_id` is `null` and was never authored (PR-5). `shares_field` is not serialized.

## NEEDS-JOSEPH (this node only)

1. **NJ-R1a-6, restated with a corpus behind it.** The addressee of a scholarship or fellowship
   application is usually a foundation, civic club, professional society, employer, or government
   program. The only target-side Applications key is `target_university`. Options unchanged:
   (a) sponsor names are values of `target_university`, (b) rename the key to a broader target
   concept, (c) a `role_split` sibling. This node ships against the existing key. My own reading
   after building the fixtures: (b) is the cheapest, because nothing except the key's spelling
   changes under any option, and (c) would put two nearly identical keys into the one table D6
   exists to keep single.
2. **Cycle-first or sponsor-first?** This node recommends cycle-first and flags it as a departure
   from `00`'s document-domain rule. It should be tested against a real scholarship corpus on the
   canvas before R1c treats it as settled. If Joseph prefers the schema's institution-first
   default here, the node still stands on its detection signals and privacy rules; only
   `template.dimension_order` and `time_first` change.
