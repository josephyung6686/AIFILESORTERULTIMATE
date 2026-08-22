# Lab notes — `academic.iep-accommodation-plans`

Date: 2026-08-22 · R1b, one roster row · kind `template`, `schema_id: academic`, launch `placeholder`

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every span I put inside quote
  marks was grep-verified against this file **before** it was written into either output. 39
  candidate spans were checked mechanically; all 39 matched verbatim, including the two carrying
  curly apostrophes. No span was paraphrased inside quote marks and none was invented.
- `planning/prompts/ALIGNMENT.md` — the two-roster-kinds rule, and "work types are values".
- `planning/domains/_CONTRACT.md` — entry shape; rules 6, 8, 11–15.
- `planning/domains/CONNECTION.md` — sections 2 (node test), 4 (activation, never-alone,
  grouping firewall), 5 (closed edge vocabulary and its kind constraints), 6 (canonical fields),
  7 (four objects), plus PR-1, PR-4, PR-6, PR-7.
- `planning/domains/CONNECTION-EXAMPLES.md` — fixtures 3 (name alone), 5 (`.ics`), 6 (`HW 3`),
  7 (one Academic schema, split by template).
- `planning/domains/roster.json` — confirmed my row, its `schema_id`, and every neighbour id I
  cite. Confirmed the **kind** of each neighbour before authoring an edge to it.
- `planning/domains/canonical_fields.json` — every `facts_legal` entry and both dimensions
  resolve to a key here. I minted nothing.
- `planning/domains/nodes/academic.json`, `medical.json`, `legal.json` — the three landed
  neighbour files. Aligned to them; rewrote none.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`, checked programmatically against all 13
  file examples.

`planning/01-product-design-structured.md` was **not** read. Everything the dispatch prompt cites
it for (§3.5 pattern-plus-context, §3.8 role split, §5.7 parent-dimension rule, §7.3's nine
residual names) is present verbatim in `00`, which wins on conflict, and CONNECTION.md already
carries the § locators. Reading a numbered rendering to re-find sentences I had verified in the
authority would have added a second vocabulary, not a second source.

Structural self-check was run as a script, not by eye: all 13 `source_type`s in `SOURCE_TYPES`;
all `facts_legal` keys canonical; both `dimension_order` entries canonical **and** declared by the
Academic schema; every `collides_with` id on the roster **and** of kind `template`; every residual
name one of the nine, spelled `00`'s way; `fields`, `proposed_fields`, `also_holds_with` empty by
intent. A regex sweep for bare numbers returned only quoted `00` examples (`AY 2024-25`,
`BUSIB 4300`), example filenames, prose enumerators, and `504` as the plan's name. No threshold,
no score.

## The node test — why this is a row and not padding

The roster hint calls this "a coverage gap the overnight pass missed", which is a reason to look,
not a reason to pass. It passes on all three of CONNECTION section 2's disjuncts, and would still
pass on the third alone:

1. **Detection signals differ from the schema's default template.** `academic.coursework` fires on
   a course-code-shaped token plus one of `00`'s five academic context terms. This situation has
   **no course code at all** in its central document — an annual plan spans every course — and
   fires instead on a labelled plan-and-services form structure: an eligibility statement, an
   annual-review slot, a services table, a present-levels/goals heading pair. Different structure,
   different rule family.
2. **Privacy rules differ, and this is the load-bearing difference.** `academic.coursework` falls
   through to Independent Records / Reading Inbox / Review Later. This row falls through to
   **Protected Records only** — the single-entry list is deliberate, and adding a non-protected
   home beside it would be the leak. Its `needs_llm` list carries a protected-path precondition
   that coursework's does not.
3. **Recommended dimensions differ**, and not by accident: `["school", "term"]` against the
   schema default `["school", "term", "subject", "work_type"]`, with both omissions argued in
   `template.why`.

What would have made this a refusal: if the only difference had been the work-type values (`iep`,
`504 plan`). Values are not nodes. They are listed under `work_types` on the existing `work_type`
field and licensed nothing by themselves.

## Files considered and rejected

- **A due-process complaint / hearing request over a denied plan.** Real, and it belongs to
  someone's corpus. Rejected as a file example here because its decisive structure is a legal
  caption, a matter identifier and a hearing officer — that file's home is
  `legal.personal-legal-matters`, and putting it in my list would have been claiming the node by
  labelling the neighbour's evidence.
- **A district special-education policy handbook, and a blank plan template.** Kept as a
  `needs_llm` line (topic-versus-record) rather than as a file example, because neither is a
  record about a named student and neither should ever activate this row. They belong in the
  discrimination, not in the coverage.
- **A `.dcm` or other clinical imaging binary.** That is `medical.json`'s example and its correct
  outcome is Unsupported or Encrypted. Nothing about it is educational.
- **A college-application disability-disclosure essay.** Its decisive evidence is a target
  institution plus admissions framing; `purpose` and `target_university` are College-applications
  fields and PR-1 forbids minting a per-domain `purpose` clone to reach it from here.
- **A contacts export (`.vcf`) of the plan team.** `00` keeps address-book data
  "privacy-protected rather than used to create folder proposals", so `contacts` is absent from
  `file_kinds.source_types` entirely rather than listed and then disclaimed.
- **A `presentation` — a transition-planning slide deck.** Plausible but thin; I would have been
  padding the source-type coverage rather than describing a file people actually keep.

The 13 that survived cover the required ugly cases: labelled form (`IEP 2025-2026`) versus
unlabelled prose (`Ms Alvarez note.docx`); a camera photo of the same page (`IMG_7741.HEIC`) and
an OCR'd portal screenshot; an archive read from its manifest with **mixed-owner members**
(`sped_packet.zip`); calendar and email; a file that *is* another node's
(`Syllabus BIOL 1201` — the collision fixture); and a file that is genuinely two schemas at once
(`Psychoeducational Evaluation`, academic and medical on disjoint evidence).

`Accommodation confirmation - Kyoto.pdf` earns its place as the never-alone fixture: the single
word this node is tempted by, in a **title zone** (so positional weighting does not save us),
attached to a hotel booking. The syllabus boilerplate paragraph is the same trap at corpus scale —
nearly every syllabus in a student's corpus contains it, so a naive rule for this node would
misfire on hundreds of files at once. Those two are why `never_alone`'s first entry is the word
itself rather than a formality.

## `proposed_fields` — none, and that is the finding

I proposed no field. The gap I hit is real and I am recording it rather than filling it: **no
canonical field names the person a record is about.** For this situation that is not a nuisance,
it is the discriminating dimension — a household with two children wants to split by child — and
it is the one dimension that must not be offered, on two independent grounds: `00` says "It should
avoid using authorship or creator identity as a destination dimension", and a child's name beside
a plan document publishes a disability determination as a folder label.

`medical.json` opened the identical fork from the health side and refused to guess. Minting
`student` or `record_subject` here would have (a) pre-empted a question two nodes now depend on,
(b) risked a synonym pair the moment medical answers it differently, and (c) produced a field
whose only obvious use is the leak. It is `open_question` (3 joined parts), not a proposal.

The same discipline applies to `school`. Its canonical role reads "the institution the holder
attends, attended, or teaches at — the person's own school", and on a parent-held plan the school
is the child's. I used `school` for the issuing/administering school and flagged the tension,
rather than minting a second spelling — a second spelling of `school` is precisely the defect D6's
ratification exists to kill.

`proposed_context_terms` is populated (20 terms) and is explicitly marked in the node as proposed:
the deterministic list says so inline, so no reader can mistake it for a vocabulary `00` wrote.
`00`'s five academic context terms are the design floor and I did not pretend it listed more.

## Neighbours considered that did **not** get an edge

- **`medical` and `legal` (my two `must_consider_neighbors`) — both schemas, so no edge from this
  row is expressible.** CONNECTION section 5 and `_CONTRACT` rule 14 are explicit:
  `collides_with` joins **same-kind** pairs and `also_holds_with` joins **schemas only**. This row
  is `kind: template`. I therefore routed each crossing to the correct kind rather than forcing it:
  - the medical crossing became a **template↔template** collision with
    `medical.dependant-child-health`, which is the roster row that actually holds the confusable
    evidence (a child's evaluation held by a parent);
  - the schema-level academic↔medical co-activation already exists — `medical.json` authored
    `also_holds_with → academic` one-way and its own note says R1c owes the reciprocal on the
    landed `academic` node. My row inherits that join through `uses_schema`; authoring a copy here
    would have been a second vocabulary for one edge.
- **`legal` got no edge at all.** The real crossing (a due-process filing, a mediation agreement,
  a settlement over services) is an **also-holds** shape, not a mutex — the file is legitimately
  both — and also-holds joins schemas. It belongs on the academic↔legal *schema* pair, which is
  R1c's to author, not on this template. Writing `collides_with legal.personal-legal-matters`
  would have been using the mutex edge to mean "related", which CONNECTION section 9 names as a
  forbidden failure mode. **Flagged for R1c:** academic↔legal is currently unasserted in both
  directions and this node is one of the reasons it should exist.
- **`academic.transcripts-credentials`** — a transcript and a plan can sit in the same district
  packet, but no single evidence item confuses them (registrar language and a grade table versus a
  services table). Co-occurrence is a grouping fact, not a collision.
- **`academic.teaching`** — a teacher's own copy of a student's plan. Genuinely adjacent, but the
  discriminating evidence is identical to the `academic.coursework` collision already authored
  (a record about one named student versus course material), so a fourth near-duplicate edge would
  have added noise rather than a discrimination. Noted, not authored.
- **`academic.homeschool`** — a parent-run schooling row that also holds child records. No shared
  confusable evidence item: homeschool material has no school-issued plan structure.

## Where I followed CONNECTION over the dispatch prompt

The dispatch prompt's edge table describes `also_holds_with` as "One file may legally carry
**both** schemas", which is the schemas-only rule stated in prose; `_CONTRACT` rule 14 states it as
a constraint. Where a reader might have taken the prompt's per-node licence to author
`also_holds_with medical` from a **template** row, I did not — CONNECTION wins, and the prompt's
own instruction says to note it here. The file-level `also_schema: "medical"` on two examples is a
different object: it records that one file may carry two schemas, which is exactly what
CONNECTION-EXAMPLES fixture 2 records, and it asserts no roster edge.

I also did not author `parent_id` (PR-5: R1b never does), did not author `shares_field` (derived
only), and set `role_split: []` — a role_split names two canonical field keys and the pair this
node would want does not exist yet.

## NEEDS-JOSEPH — this node only

**NJ-IEP-1 · Does a holder-versus-subject role split enter the canonical field list?**
Three questions in one, and the third is the one that bites:

1. Does the canonical list gain a field for *the person a record is about*, distinct from
   `authored_by`? `medical.json` asks the same thing from the health side; one answer serves both,
   and two answers would be a synonym pair.
2. If it lands, is it destination-eligible for this template or metadata-only? This row's
   `dimension_order` assumes **metadata-only**, because as a folder label beside a plan document a
   child's name publishes a disability determination in a namespace Finder, Spotlight, backup and
   sync clients all read.
3. Does `school` need re-reading for parent-held records? Its canonical role says "the person's
   own school"; here it is the child's. I used it as the issuing school and flagged the tension
   rather than minting a synonym.

**NJ-IEP-2 · Is `work_type` metadata-only for this template, as recommended?**
The row omits `work_type` from `dimension_order` on privacy grounds while keeping it as an
extractable fact. That is a deliberate use of P10's `metadata_only` mechanism (CONNECTION section
6) and it costs the user a level they might genuinely want. If Joseph decides that a folder named
for the record kind is acceptable in a local-only protected branch, restoring it is a one-line
change to `dimension_order` — but it should be his call, not this node's, because it is the
question of whether a protected branch's own labels may name what the protection hides. `00` is
suggestive but not decisive: "Protected branches should have configurable redaction in the canvas
and review screens" is about the product's screens, not the filesystem.
