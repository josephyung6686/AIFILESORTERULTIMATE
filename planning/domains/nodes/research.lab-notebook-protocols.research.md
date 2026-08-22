# research.lab-notebook-protocols — lab notes (R1b)

Roster row: `kind: template`, `schema_id: research`, `launch: full`, `provenance: inference`,
`must_consider_neighbors: [medical]`, `must_consider_residuals: [Review Later]`.
Verdict: **node kept** (`refuse_node: false`). Reasoning is in the node file's `node_test` block;
this file records the working, the rejections, and the questions.

## Sources used

- `planning/00-database-agent-product-design.md` — read in full; the authority for everything
  marked `design`. **Every quoted span in the node file was grep-verified against this file before
  it was written**, and re-verified mechanically after writing (a script walked every string in
  the JSON, pulled every `"…"` span, and matched it against `00`: 0 misses).
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md` (fixtures 1–2 and
  the HEIC / no-EXIF pair).
- `planning/domains/roster.json` — confirmed the id, kind, schema, and every edge target's
  existence and kind.
- `planning/domains/canonical_fields.json` — confirmed `lab`, `project`, `artifact_type` are
  canonical and `destination_eligible: true`; confirmed there is **no** destination-eligible time
  field available to this schema.
- `planning/domains/nodes/research.json` (the schema) and
  `planning/domains/nodes/research.project-workspace.json` (the refused sibling) — read in full,
  to make sure this row is not a third copy of the same default. Skimmed
  `planning/domains/nodes/academic.coursework.json` for the shape of its `collides_with` signals.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked mechanically against every
  `file_examples[].source_type` and against `file_kinds.source_types`.
- `planning/01-product-design-structured.md` — **not** read beyond what `00` already settled;
  nothing in this node rests on it, and `00` wins on conflict.

## Why the node survives the node test

The sibling `research.project-workspace` was refused for being the schema's default template in a
template's clothing. This row is not that, and the difference is one concrete fact about the
material: **bench material is owned by a lab, not by a project.** One RNA-extraction SOP serves
three projects; an instrument export belongs to a run, not a manuscript; a notebook page predates
the project it eventually feeds. That single fact drives all three limbs:

- **signals** fire without a project token, which every deterministic signal on the research schema
  row requires;
- **dimensions** lead with `lab` and drop `stage` (a standing procedure has no workflow position);
- **privacy** hangs on inline participant identifiers in files with no form structure — unlike
  `research.ethics-compliance`, whose material announces itself with labelled approval slots.

Had those collapsed, the honest output was a refusal; the refused sibling next door is the
evidence that refusing was a live option here rather than a formality.

## Files considered and rejected

- **`PVA-RDP_manuscript_v7.docx`, `submission.zip`, referee correspondence** — `research.manuscript-publication`.
  Nothing bench-shaped about them.
- **`Abstract_PVA-RDP_UChicago.pdf`** — `research.conference-presentation` / the
  `college_applications` two-schema case. Already worked on the schema row; re-using it here would
  have padded the list without testing this row.
- **`Ravikumar_2019_NatureMethods.pdf`** — `research.reading-library` → Reading Inbox. A method
  paper *reads* like a protocol, which tempted me, but the discriminator is authorship, not
  structure, and that discrimination lives on the schema row's `authored_by`.
- **`analysis/train_eval.py`, `results_batch07.xlsx` (computed sheets)** — `code` /
  `research.dataset-analysis`. I kept only the *provenance* workbook (`SampleLog_…`) and turned the
  seam into a `collides_with` signal rather than claiming both.
- **`Consent_form_participant_04.pdf`** — `research.ethics-compliance` outright; no shared evidence
  item worth a fixture beyond the IRB protocol I did keep.
- **`Freezer_inventory.csv`, `Reagent_order_INV-2291.pdf`** — the first is a thinner duplicate of
  the sample log; the second is a purchase record that belongs to Receipts and Confirmations or a
  finance template, and including it would have argued for a field this schema does not have.
- **`Gel_image_raw.tif` beside `IMG_4102.HEIC`** — same evidence, one fixture is enough; the HEIC
  is the sharper one because `00` requires HEIC support explicitly and because camera EXIF makes
  the photos reading genuinely correct rather than a mistake to suppress.

Twelve fixtures survived. Four exist only to be *refused* by this row: the recipe scan (structure
without role), the course lab report (neighbour), the IRB protocol (sibling), and the `.ics`
booking (format alone).

## `proposed_fields` — none, and why

Three keys were genuinely tempting and all three were rejected:

- **`instrument` / `facility`** — the producing device or core facility. Rejected: it is an
  organization-or-creator value, and `00` puts creator identity outside destination dimensions
  outright. Where a facility must be named, it is a **value** of the existing `lab` key, which is
  what the "lab is doing two jobs" note below is about.
- **`sample_id` / `specimen_id`** — rejected as a schema field: it is a per-row datum inside a
  workbook, not a fact about the file, and turning per-row identifiers into a field is how a
  privacy leak becomes a folder level. It stays an observation that supports `project` and
  `artifact_type` and supports P9 grouping (a run neighbourhood), nothing more.
- **`protocol_version` / `effective_date`** — rejected: the universal `version_family` fact
  already carries the first, and a date is a universal fact. Minting a date key here is precisely
  the open question below, and closing it silently would be the 574's failure at one-node scale.

So `proposed_fields: []`. The bench-specific `artifact_type` **values** (instrument export, sample
log, calibration record, safety or training record, bench photo) are recorded in
`work_types_note` as a value-list note for R1c — values, not keys.

## Neighbours considered that did *not* get an edge

- **`medical` (the roster's `must_consider_neighbors` entry) — no edge, deliberately.** `medical`
  is a `kind: schema` row; `_CONTRACT.md` rule 14 and `CONNECTION.md` §5 make `collides_with`
  same-kind-only and `also_holds_with` schema-to-schema-only, so a template may not point at a
  schema with either. The relationship is real and is honoured twice: the collision lands on
  `medical.personal-health-records` (the medical schema's template row, same kind), and the
  research↔medical `also_holds_with` already exists on `research.json`, which is its correct home.
- **`academic` (schema)** — same reason; the collision lands on `academic.coursework`, the template.
- **`research.project-workspace`** — refused as a node, so no edge to it. Its `Protocol_RNA-extraction_v2.docx`
  fixture explicitly hands this material to this row, and I kept the same filename so the two files
  read as one story.
- **`research.manuscript-publication`** — considered and rejected. A figure panel travels from a
  bench image to a manuscript figure, but that is a **derivation over time**, not one evidence item
  supporting two readings, so it is not what `collides_with` means under the narrowed definition.
- **`photos` / `photos.camera-events`** — `IMG_4102.HEIC` really does carry both readings, but on
  **disjoint** evidence (camera EXIF versus the label card and the run neighbourhood), which is
  `also_holds_with` semantics, not a collision. Since a template cannot author `also_holds_with`,
  it is recorded as `also_schema: "photos"` on the fixture and reported here for R1c: **the
  research↔photos `also_holds_with` pair is missing from `research.json` and is worth adding at
  merge time.**
- **`finance` / `finance.receipts-expenses`** — reagent purchase records touch it; excluded with
  the fixture that raised it.

### Where CONNECTION.md and the dispatch prompt disagree

The prompt's edge table describes `also_holds_with` as "One file may legally carry **both**
schemas" and invites it on any node. `CONNECTION.md` §5 restricts the edge to `schema ↔ schema`
and `collides_with` to same-kind pairs. **CONNECTION wins**, per the prompt's own closing rule, so
this template authors `also_holds_with: []` and routes its two genuine dual-schema files through
per-file `also_schema` annotations instead. Noted here as instructed.

## Findings for R1c

1. **`research.json`'s `falls_through_to` is incomplete** — it omits Review Later and Protected
   Records, and Review Later is the roster's own must-consider residual for this id. The refused
   `research.project-workspace` node raised half of this already; this node raises the other half
   (Protected Records, for participant-identified bench records).
2. **research ↔ photos `also_holds_with` is missing** on the research schema row (bench photo with
   camera EXIF). See above.
3. **`file_kind_owner` ambiguity, third sighting.** The roster gives `spreadsheet` to
   `research.dataset-analysis`, `image` to `photos`, `ocr` to the photos capture templates — yet a
   sample log, a bench photo and a scanned notebook page are this situation's core material. This
   node handles it by making the discriminator explicit in `collides_with` signals rather than by
   claiming ownership. Whether `file_kind_owner` is exclusivity or primary interest still needs
   settling.
4. **`lab` is doing two jobs in bench material**: the group that *owns* a protocol and the core
   facility that *ran* an instrument. Reported, not minted — it is a value-resolution question, and
   a second key would be a private field.
5. **`role_split` for `lab ↔ school`** is recorded on `research.json` but the canonical row for
   `lab` still carries an empty `role_split_with`. Unchanged by this node; repeated so it is not
   lost.

## NEEDS-JOSEPH (this node only)

- **NJ-lab-1 · Time as a dimension for chronological bench records.** A lab notebook is
  chronological by construction, and its owner refers to "the March 2026 notebook". The research
  schema declares **no destination-eligible time field**: `capture_year` is the photos schema's,
  `term` is academic's, `tax_year` is finance's, and `creation_date` is a universal seeded
  `destination_eligible: false`. So this template cannot offer a date level at all. Does the
  research schema gain a destination-eligible time field for bench records, or is the honest answer
  that notebooks branch by lab and project and stay chronological only *inside* a folder? Not
  resolved here: minting a time key on a template row is exactly the private-field failure R1
  exists to prevent, and the answer decides someone's real folder structure.
- **NJ-lab-2 · Is a PI-named lab an organization or creator identity?** This row puts `lab` first,
  which sharpens the hazard `research.json` already recorded. If a PI-named lab reads as creator
  identity, `00` forbids it as a folder level and this row's entire recommended order has to be
  re-derived (most likely to `project → artifact_type` with `lab` metadata-only). The question is
  inherited, but this node is the one whose recommendation depends on the answer.
