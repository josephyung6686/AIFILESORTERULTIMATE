# applications.purpose-packet — lab notes

Date: 2026-08-22
Row: `kind: template`, `schema_id: college_applications`, `launch: full`, node **accepted** (not refused).
Output: [`applications.purpose-packet.json`](applications.purpose-packet.json)

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full; the authority. Every one of the 75
  quoted spans in the JSON was grep-verified against this file mechanically before the file was
  written, and the check was re-run after the one edit (a trailing period that `00` writes as an
  em dash). Zero unverified quotations.
- `planning/01-product-design-structured.md` — §5.6 (Applications and purpose-defined packets),
  §5.7 (template library) only, plus the section index to locate them. `00` wins on any conflict;
  none arose — §5.6 is a verbatim rendering of `00`'s own paragraph.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md` (fixtures 2, 3, 6, 8
  are the ones this row has to stay compatible with).
- `planning/domains/roster.json` — confirmed id, kind, `schema_id`, neighbours, and
  `file_kind_owner: ["archive"]` on this row.
- `planning/domains/canonical_fields.json` — every field key referenced resolves here. Nothing
  minted.
- `planning/domains/nodes/college_applications.json` (my schema) and
  `planning/domains/nodes/applications.undergraduate-packet.json` (my sibling, already landed —
  it authored a collision edge at me, which I reciprocate), plus the collision surfaces of
  `academic.transcripts-credentials.json`, `academic.coursework.json`, `identity.json`.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`, checked programmatically against every
  `file_examples.source_type` and `file_kinds.source_types` member.

## The node test — why this row is not a refusal

The schema's default template (and the sibling `applications.undergraduate-packet`) fires on a
**resolved addressee institution** and branches `target_university → application_cycle →
application_document_type`. This row fires on the **absence** of one, and all three of the node
test's discriminators are present:

1. **Detection signals differ.** Archive manifest read without unpacking (`00`'s `submission.zip`
   sentence, and the roster gives this row `file_kind_owner: ["archive"]`); an existing
   user-created folder whose name expresses purpose rather than an institution (`00`'s
   `Chinese University Application Materials` directory); a co-present set of compatible record
   types under submission language.
2. **Recommended dimensions differ.** Flat, led by `purpose`, one level. `00` states it:
   "The user may keep it as one flat purpose folder".
3. **Privacy rules differ.** The packet is sensitive *by composition* (its defining member list
   includes an identification document), and the archive that carries it is inspected without ever
   being extracted to disk. Neither constraint exists on the institution-first situation.

## Files considered and rejected

- **`Wash U.docx`** — `00`'s own file, but it is single-addressee prose. It belongs to the sibling
  row, which already uses it. Including it here would have been padding with someone else's fixture.
- **`Screenshot ... "Your Columbia University application has been submitted"`** — same reason: one
  institution resolves, so it routes away. I used a *checklist* capture with no institution instead,
  which is the capture this situation actually produces.
- **`Duke Why Us Essay.docx`** — the conflicting-addressee outlier. It is a real constraint for this
  template (a packet must not absorb it) so it appears in `validation_constraints`, but as a
  *file example* it is the sibling's and the schema's.
- **A `.ics` interview invite** — the schema row already carries one, and a calendar event names an
  institution, which routes away. Dropping it also keeps CONNECTION-EXAMPLES fixture 5 honest:
  `calendar` is a `SOURCE_TYPE`, not evidence of a packet.
- **A `.vcf`** — `00` says contact data "should normally be privacy-protected rather than used to
  create folder proposals"; it has no role in this situation at all.
- **A tax return / financial-aid form** — real packet members in some corpora, but the discriminator
  work belongs to `finance.student-financial-aid`, and the sibling already authored that collision.
  Left out deliberately rather than duplicated.

The eleven that survived cover: labelled form/checklist slot vs unlabelled prose (`Checklist
screenshot.png` vs `个人陈述.docx`), OCR of the same class of thing (`Scan 001.pdf`, `ID card
scan.jpg`), the archive packet with mixed members (`submission.zip`), mail (`Documents received -
application submitted.eml`), a look-alike that belongs to a neighbour (`Job Application -
Deloitte.zip`), a file that is *also* another domain (`PVA-RDP Abstract.pdf` → research;
`Transcript.pdf` → academic; `ID card scan.jpg` → identity), the unreadable case (password-protected
`Application Materials.zip`), and the sparse `HW 3`-shaped file (`Scan 001.pdf`, which takes a
membership record and no facts).

## proposed_fields — none, and why

`proposed_fields` is empty. The four inherited keys (`target_university`, `application_cycle`,
`application_document_type`, `purpose`) plus the schema's `school` and the universals cover every
fact in every file example. The one thing this situation seems to want and does not get is a field
for *the packet itself* — a submission id, a platform, a deadline. Each was rejected:

- a **submission id** is a value, not a field the tree could ever branch on, and `00` allows new
  values freely while forbidding automatic new fields;
- a **platform/system** name is the same role `target_university` already holds and would be a
  second column for one concept — D6's exact defect. The tension (an addressee that is not a
  university) is already recorded as an open question on the schema row and on
  `applications.scholarship-fellowship`; adding a field here would silently close it;
- a **deadline** is a date, and `00`'s narrow-date rule plus the absence of any template that
  branches on it makes it a search field at best.

## Neighbours considered that did **not** get an edge

- **`research` / `research.project-workspace`** — the PVA/RDP abstract is the archetypal member of
  this packet, but the evidence is **disjoint** (project identifier from the document; submission
  context from the packet), which is `also_holds_with`, not a collision. Per CONNECTION.md §5,
  `also_holds_with` **joins schemas only**, and my schema `college_applications` already carries it
  to `research`. So this template authors nothing and keeps `also_holds_with: []`. The physical-home
  question for that file is `00`'s shared-material policy, decided at P10/P11, not an edge here.
- **`academic` / `identity` as schemas** — same reason. My `must_consider_neighbors` names schemas,
  but a template's `collides_with` may only join same-kind rows, so those three were resolved to
  template ids: `academic.transcripts-credentials`, `identity.core-documents`, and (for the resume)
  `career.recruiting`.
- **`finance.student-financial-aid`** — a genuine member type, but the discriminating evidence is
  identical to the one the sibling already authored, and inheriting a collision I did not need
  would add reciprocity debt without adding a discriminator. Flagged here for R1c rather than
  authored.
- **`applications.k12-admission` / `applications.scholarship-fellowship`** — both appear in
  `routes_away_when` (their discriminators are the applicant's relation to the holder, and the
  addressee's role) but not as collisions: the confusion is with the *institution-first* rows, not
  with a flat packet, and both are placeholder-launch rows that have not landed.
- **`photos.screenshot-captures`** — the checklist capture falls through to Temporary Screenshots
  when its OCR yields nothing, which `falls_through_to` already expresses. A collision edge would
  claim the two rows compete for the same evidence item; they do not.

## Where this prompt and CONNECTION.md disagreed — CONNECTION won

1. The dispatch prompt lists `also_holds_with` in the edge table available to this row. CONNECTION.md
   §5 restricts it to **schema ↔ schema**. I followed CONNECTION and left it empty; the abstract /
   transcript / ID co-activations live on the `college_applications` schema row, which already
   authors all three reciprocally.
2. The prompt's example object puts `proposed_context_terms` and situation-routing inside
   `recognition`. `check.py` fails any `recognition` key outside `deterministic` / `needs_llm` /
   `never_alone`, so both live at the top level here (`proposed_context_terms`,
   `routes_away_when`). Two already-landed sibling files nest one or both inside `recognition` and
   will report findings when R1c merges them — worth a sweep, not my file to edit.
3. `parent_id` is `null` and was never a candidate: PR-5 says R1b never authors it.
4. D6/D2 as ratified: snake_case throughout, `subject` is the academic key (it appears only in a
   neighbour's discriminator here, not on this row).

## Two things this row is deliberately careful about

- **The tempting false file.** For every other applications row the trap is a bare university name.
  For this one it is a **download session**: four documents saved to Downloads within minutes look
  exactly like a submitted set. `00` rules on it twice, and both sentences are quoted in
  `never_alone`. The second trap is **record-type composition alone**, which is why
  `Job Application - Deloitte.zip` is in the file list — same manifest shape, employer addressee.
- **Membership never becomes a fact.** Four of the eleven examples carry
  `group_without_copying_facts: true`, including the ID scan and the sparse `Scan 001.pdf`. This is
  the CONNECTION-EXAMPLES fixture 6 shape transposed onto a purpose packet: the packet is exactly
  the structure that makes copying tempting, because its members genuinely belong together.

## NEEDS-JOSEPH — this node only

- **NJ-local-1 · What string names a flat purpose branch?** The recommended dimension is `purpose`
  (a normalised fact value), but `00`'s own instance of this branch is a **user folder name**
  ("an existing Chinese University Application Materials directory"), and the accepted group carries
  a **display label** ("Columbia Application — 2026 Cycle" is `00`'s shape for the sibling). Three
  strings can name one level. Every other template hides this because its first level is an entity
  name; this one cannot. Whoever owns node labelling at P10 needs an answer.
- **NJ-local-2 · A one-dimension template.** This row recommends a single level on purpose, and
  `00` supports flatness ("a two-file application packet may remain a single folder"). Confirm that
  a `dimension_order` of length one is an accepted template shape and not something a later gate
  reads as an unfinished row.
- **Inherited, restated because it lands hardest here:** NJ-3 / PR-1 scopes `purpose` to
  Applications. `purpose` is this template's **only** dimension, so if PR-1 is reversed — or if a
  purpose-coherent packet outside admissions (a visa packet, a grant submission) needs a home —
  this is the row that changes shape, not the schema.
