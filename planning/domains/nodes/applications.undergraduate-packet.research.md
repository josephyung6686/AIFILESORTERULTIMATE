# Lab notes — `applications.undergraduate-packet` (R1b, kind: template)

Date: 2026-08-22
Row: `kind: template`, `schema_id: college_applications`, `launch: full`, `provenance: design`
Output: [`applications.undergraduate-packet.json`](applications.undergraduate-packet.json)

## Sources actually read

- `planning/00-database-agent-product-design.md` — in full. Every span in quote marks in the node
  file was grep-verified against it **before** it was written; a script then re-extracted all 48
  quoted spans from the finished JSON and re-checked each one (0 misses).
- `planning/domains/_CONTRACT.md` (entry shape, rules 8/11–15), `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md` (all eight fixtures).
- `planning/domains/roster.json` (my row, the four sibling application templates, every id I
  reference), `planning/domains/canonical_fields.json` (no key was minted).
- `planning/domains/nodes/college_applications.json` — my schema, already landed. I aligned to it
  and rewrote nothing in it.
- `planning/domains/nodes/academic.coursework.json` + its research notes — it had already authored
  a `collides_with` edge naming this id, and its role_split names this id. I reciprocated both.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked mechanically against every
  `file_examples[].source_type` and `file_kinds.source_types` member.
- `planning/01-product-design-structured.md` — not read beyond confirming it is a rendering of
  `00`; `00` was authoritative for everything here and nothing in this node depends on a §-number.

## The node test — why this row was not refused

This was a genuine refusal candidate, and I nearly refused it. The dimension order I recommend
(`target_university → application_cycle → application_document_type`) is *identical* to the inline
`template` block on the `college_applications` schema row, which is `00`'s own Applications
default. Under the prompt's refusal clause a template must differ in detection signals, dimension
order **or** privacy rules. Dimension order does not differ. Two other things do:

1. **Detection is strictly narrower than the schema's, in a way that routes.** The schema must
   activate across five sibling situations (flat purpose packet, graduate/professional, K-12
   admission, scholarship/fellowship, and this). This template fires only when the evidence
   resolves **exactly one addressee institution** for the file or branch, and its
   `recognition.routes_away_when` block sends the other four away explicitly — no single addressee
   → `applications.purpose-packet`; sponsor addressee → `applications.scholarship-fellowship`;
   SOP/CV/writing-sample set → `applications.graduate-professional`; guardian-held minor →
   `applications.k12-admission`. Those are routing rules a schema row cannot hold, because the
   schema must admit all of them.
2. **It carries a validation constraint only institution-first organisation creates.** The first
   folder level *is* `target_university`, which makes packet membership a standing temptation to
   write that fact onto a shared transcript, resume or platform document. `00` answers it twice —
   "an application packet does not silently absorb a document with a conflicting target
   institution" and, for the shared case, "If no shared branch exists, the system should not
   arbitrarily choose one university. It should abstain or ask the user to choose a primary home."
   The flat purpose packet has no such constraint because it has no institution level. This is the
   node's real content, and it is why `never_alone` carries a packet-membership clause the schema
   row states as an activation rule and this row states as a destination rule.

A third, weaker leg: the applicant here is the holder and an adult-facing privacy default applies,
which is exactly the axis `applications.k12-admission` differs on.

**Recorded honestly, not resolved:** two rows now state one dimension recommendation. That
duplication is real and it is this node's `open_question` for R1c/Joseph — the same open question
`academic.coursework` recorded against `academic`. I did not resolve it unilaterally in either
direction, and I did not manufacture a different dimension order to create an artificial
difference: `00` states this order for this situation, and inventing a divergence to pass a test
would be the padding failure in a different costume.

## Files considered and rejected

- **`submission.zip`** — `00`'s own archive case. Rejected as *this* template's evidence: the
  roster gives `archive` `file_kind_owner` to `applications.purpose-packet`, and an archive whose
  manifest names no single addressee is precisely what routes away from institution-first. It
  survives in the file list only as `Application Materials.zip`, a **routing-away fixture** whose
  `must_not_conclude` says this template does not apply. `archive` is therefore deliberately absent
  from `file_kinds.source_types` while appearing once in `file_examples` — intentional, noted on
  the row.
- **`Wash U.docx`** — kept as a `needs_llm` signal, not duplicated as a file example: it is the
  schema row's load-bearing fixture and repeating it would add nothing this row does not already
  test through `Essay Draft 2.docx` (the sparse case) and `Why Columbia - final.docx` (the
  resolved case).
- **A `.vcf` of an admissions counsellor** — rejected. `00`: contact data "should normally be
  privacy-protected rather than used to create folder proposals", so it evidences nothing here and
  a contacts example would only restate a rule that lives on the schema and in CONNECTION fixture 6.
- **A recommender's letter PDF itself** — rejected as a file example because in the real corpus the
  applicant almost never holds it (it is submitted directly). The *request email* is what the
  holder has, and it is the better authorship-as-destination fixture.
- **`Portfolio.pdf` / arts supplement** — considered; it is a value of
  `application_document_type` (`portfolio submission`, listed under `work_types`), not a file whose
  observations teach anything the essay and checklist fixtures do not.
- **An acceptance letter as a separate example** — folded into `work_types` (`decision letter`) and
  into the portal-capture fixtures; a fourteenth near-duplicate text_document would be padding.

## `proposed_fields` justification

**None proposed.** Every fact this situation needs is already canonical: the four inherited keys
(`target_university`, `application_cycle`, `application_document_type`, `purpose`), plus `school`
(the role-split counterpart, declared on the schema row and used by the transcript fixture),
`version_family` and `sensitivity_status` (universals). The one field tension in this area —
`target_university` holding an addressee that is not a university — belongs to
`applications.scholarship-fellowship` and is already recorded on the schema row and in ROSTER.md;
minting a field here to "fix" it would be exactly what `_CONTRACT.md` rule 8 forbids.
`proposed_context_terms` are marked as proposal, not design, and carry no regex and no threshold.

## Neighbours considered that did NOT get an edge

- **`research` / `research.manuscript-publication`** — `00`'s PVA/RDP abstract is Research *and*
  Applications. That is `also_holds_with`, and CONNECTION.md §5 restricts `also_holds_with` to
  **schema ↔ schema**; it is already authored on `college_applications.json`. So no edge here.
- **`identity.core-documents`** — an application packet legitimately contains an ID document; again
  a schema-level `also_holds_with` (already on the schema row), not a template collision. The ID
  case survives here through `falls_through_to: Protected Records` and the CSS-profile fixture.
- **`academic.k12-schooling`** — the applicant's own secondary-school record. It collides with
  `applications.k12-admission` (whose applicant is a minor), not with this row, whose applicant is
  the holder. Left to that sibling rather than claimed.
- **`career.employment-records`** — a resume sits between recruiting and applications; the
  employment-records situation is about the employment relationship itself, which no undergraduate
  application document evidences. Only `career.recruiting` got the edge.
- **`finance.receipts-expenses`** — an application fee receipt is a receipt; `00` gives it a
  residual home (Receipts and Confirmations) rather than making it an admissions artifact, so no
  edge and no fee-receipt fixture.
- **`photos.screenshot-captures`** — portal screenshots are captures, but the discriminator is the
  OCR content, and the screenshot-capture template's own row owns that seam; adding a duplicate
  edge from this side would assert a mutex I cannot state without seeing its signals. Left for R1c
  reciprocity if that row claims it.

## Where CONNECTION.md overrides the dispatch prompt

The prompt offers `also_holds_with` in its edge table for any node. CONNECTION.md §5 restricts it
to **schema ↔ schema only**, and restricts `collides_with` to **same-kind pairs**. CONNECTION wins,
so on this template row:

- `also_holds_with` is **empty**. The co-holding facts that are true of my fixtures
  (`Transcript.pdf` → academic, `CSS Profile Summary.pdf` → finance) are recorded through
  `file_examples[].also_schema`, which is a fixture annotation and not an edge.
- `collides_with` names **template ids only** — all nine verified `kind: template` on the roster.
  My roster row's `must_consider_neighbors` gave me the *schema* ids `academic` and `career`; I
  resolved each to the template rows that actually hold the confusable material
  (`academic.coursework`, `academic.transcripts-credentials`, `academic.standardized-testing`,
  `career.recruiting`).
- `parent_id` is `null` and was never authored (PR-5: R1b never authors it).
- `falls_through_to` uses the object form (`residual_template` + `why`) that the sibling template
  row `academic.coursework` uses, so R1c merges one shape; the names are `00`'s nine, spelled
  `00`'s way. The schema row uses bare strings — a cosmetic divergence for R1c to normalise.
- `shares_field` is not authored anywhere (derived only).

## Mechanical checks run

- JSON parses; **no numeric value anywhere** in the file (script-checked).
- All 15 `file_examples[].source_type` values ∈ `SOURCE_TYPES`; `file_kinds.source_types` ⊆
  `SOURCE_TYPES`.
- All `facts_legal` entries resolve to `canonical_fields.json` keys.
- `dimension_order` ⊆ the `college_applications` schema's declared fields **and** ⊆ canonical keys,
  and every member is `destination_eligible: true`.
- Every `collides_with.domain` and `role_split.neighbor` exists on the roster; every
  `falls_through_to.residual_template` is one of §7.3's nine.
- Every `file_examples[].must_not_conclude` begins with "a folder path"; no example writes a path
  as a fact.
- The two sparse/shared cases (`Essay Draft 2.docx`, `Transcript.pdf`, plus
  `Common App - Activities List.pdf`, `Resume 2026.pdf`, `Application Deadlines.xlsx`) carry
  `group_without_copying_facts: true` instead of an invented institution fact.
- At least one `never_alone` is true of a tempting false file: the university-name-alone rule is
  what keeps `Columbia BUSIB 4300 Syllabus Spring 2026.pdf` out, and the packet-membership rule is
  what keeps `Transcript.pdf` from gaining an addressee.

## NEEDS-JOSEPH (this node only)

- **NJ-U1 · Who owns the Applications dimension recommendation?** The `college_applications`
  schema row and this template row now state the same `dimension_order`. Either the schema's inline
  block is read as this template's definition (and the schema stops carrying one), or a schema keeps
  a default template for P10's schema-id resolution path and the duplication is accepted as
  intentional. Same fork `academic.coursework` raised against `academic`; it should be answered once
  for the whole roster, not per node.
- **NJ-U2 · Shared application material: branch, primary home, or mandatory review?** `00` names
  `Applications/Shared Application Materials` and also allows a primary-home convention, an alias
  convention, or mandatory review. Institution-first is the situation where this is forced, and
  which default the template *offers* is a decision about someone's real filesystem. This row
  offers the shared branch as an optional branch pattern and abstains otherwise; it does not pick.
- **NJ-U3 · Does an institution-named branch label need redaction?** I recorded in
  `sensitivity_why` that a branch labelled with an institution is itself disclosive on a shared
  screen. `00` asks for configurable redaction of protected branches; whether admissions branch
  *labels* fall under it is Joseph's, not mine, and P7 owns the handling class either way.
