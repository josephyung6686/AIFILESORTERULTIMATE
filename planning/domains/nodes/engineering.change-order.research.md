# engineering.change-order — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.change-order.json`](engineering.change-order.json).
Salvage: none — no prior draft existed for this id. Both files are new and owned by this pass.
Verdict: **node kept**, after the charge below came closer to killing it than any other part of this work.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped assignment from
  `make_prompt.py engineering.change-order`.
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted `grep -n`
  rather than streamed. Five spans pulled and matched verbatim (audit below).
- `planning/domains/nodes/engineering.json` — **the schema anchor, and the file that decides this
  row.** Its `template.why`, its ten deterministic signals, its `work_types[]`, its twelve file
  examples and its four `proposed_fields` are the default template this row is measured against.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the depth calibration named by the
  brief. It supplied two structural precedents used directly: a template may earn its node by
  **dropping one level** from its schema's default (that row drops `account_type`; this row drops
  `lifecycle_stage`), and an empty `proposed_fields` with an argued refusal beats a minted key.
- One grep for landed rows that already argued a boundary against this id, then targeted
  extraction from the three that named engineering: `construction_property.variation-claim.json`
  (which **already carries a `collides_with` edge pointing at this id** — reciprocated here on the
  same discriminator), `business_operations.contract-administration.json`, and
  `business_operations.product-requirements.json` (whose engineering collisions target
  `requirements-specification` and `verification-validation`, not this row — noted, not stolen).
- `planning/domains/roster.json`, `canonical_fields.json`, `src/evidence_shape/vocabulary.py` —
  edge endpoints, canonical keys and `SOURCE_TYPES` all checked mechanically.

Not read, deliberately, on the brief's token discipline: `engineering.research.md` (the JSON
settled every question I put to it), and no other row "for context".

---

## THE CHARGE — the strongest case that this row should not exist

I owe this section the most work, because on first inspection this row looks like a textbook
574-era mistake, and it is very nearly one. Six separate charges, in descending strength:

**Charge 1 — it is a work_type value, verbatim, in its own schema's enum.** The engineering
schema row's `work_types[]` contains the literal string `"engineering change request/order/notice"`.
ALIGNMENT holds that work types are values of a field and never nodes. This is not an analogy or a
near-miss: the row's name is an item in its own parent's value list. If any charge should kill a
row, this is the shape of it.

**Charge 2 — request → order → notice is a lifecycle stage.** ECR, ECO and ECN are three states of
one transaction. A row named for a stage of something else is exactly what the node test forbids,
and the engineering schema already proposes `lifecycle_stage` as a field — so this row would be a
node standing in for a value of a field its own schema declares.

**Charge 3 — it duplicates the schema's default template.** The default's deterministic list
already contains a change signal: *an engineering-change structure that identifies an affected
design item and current/replacement revision, states the technical reason and effect, and carries
disposition or approval.* Worse, the schema's own file examples already include
`ECR-1187_BPA-210_Bushing-Material.pdf`. The anchor has claimed my headline fixture. A template
whose evidence is already listed on its schema is the definition of a duplicate.

**Charge 4 — it is a document type word.** "Change order" is a form name. `00`'s discipline is
that a document-type word is evidence, not a filing world, and a row whose only content is a
document-type word can never activate on anything but that word.

**Charge 5 — it duplicates neighbours.** `construction_property.variation-claim` holds
"variation orders and their registers"; `business_operations.contract-administration` holds "the
variations and change orders that amend it". Two landed rows already say they hold change orders.

**Charge 6 — it is a row defined by an absence.** One could read it as "the engineering files that
are not the design itself" — a negative definition, which the brief names as a refusal trigger.

### Why the charges fail

Charges 4 and 6 fail immediately and are the weakest: the row is not defined by the word or by an
absence, but by a **structure** — see the three signals below that the word "change" never
produces on its own, and the ten `never_alone` rules whose whole purpose is to stop the word firing.

**Charges 1 and 2 fail on the same fact, and it is the fact this row is built on: a change is not a
file, it is a multi-file, multi-item transaction.** A `work_type` value describes what one file
*is*. ECO-1187 is not one file. It is a request, an impact assessment, a set of redlines, board
minutes, an approved order, a distribution mail and an archive package — seven artifacts carrying
at least five *different* `work_type` values, which nonetheless file together and are retrieved
together. No value of a field can express "these seven heterogeneous files are one object". That is
what a template is for. And charge 2 collapses at the same point: this row explicitly **refuses to
split on stage**. `ECR-1187` and `ECO-1187` are both listed as file examples and both file
identically. A stage-shaped node could not do that; it would have to put the request somewhere else.
The request/order/notice progression is a value of a disposition slot inside the row, not a
boundary between rows.

**Charge 3 — the serious one — fails on two independent legs of the node test, argued in full below.**
The schema's one change signal is the schema proving it *can* activate on change material. It is
not a filing rule, and it says nothing about dimensions. Where the schema anchor lists
`ECR-1187_BPA-210_Bushing-Material.pdf`, this row keeps that exact fixture deliberately, so that
the same bytes are argued on both sides: the schema uses it to show engineering fires; this row
uses it to show that the change files differently from what it changes.

**Charge 5 fails on discriminating evidence and is now reciprocal in the JSON.** Both neighbours
hold change *documents*; neither holds a change to a *released design definition*. The
discriminators are named in both directions, on the same fixtures, below.

The row survives. It came closest to dying on charge 3, and if the two dimension-order and
detection differences below had not been real, the honest outcome would have been
`refuse_node: true` with the coverage routed to the schema default and `Independent Records`.

---

## The node test, argued in full

CONNECTION.md's test: a template exists only when its detection signals, its recommended
dimensions, or its privacy rules differ from its schema's default template. Two of three differ
substantively; the third differs in kind and is argued rather than leaned on.

**Leg 1 — detection signals: DIFFERENT.** Four structures discriminate this row that the schema
default never names, each chosen because it is absent from every other engineering artifact:

1. *A from/to supersession pair on one item identifier.* A released drawing carries its own
   revision. Only a change record carries a **predecessor and a successor** for the same item. This
   is the single sharpest signal on the node, and it is why a bare `Rev C` token is a `never_alone`.
2. *An affected-documents table.* Its rows are **other artifacts** — a drawing number, a product
   structure, a specification, a work instruction, each with its own revision. This makes the change
   record a manifest of pointers rather than a document with technical content, which is a
   structural fact with a filing consequence (see grouping, below).
3. *An effectivity slot* — from which serial, lot, date or on-exhaustion-of-stock. No requirement,
   drawing, analysis or verification report has a from-which-unit slot. It is also the honest join
   to manufacturing and the reason `manufacturing` is an `also_holds_with` rather than only a
   collision.
4. *A disposition bound to an approval roster.* Every engineering artifact has an approval block;
   only this one records **a decision about whether something may change**, which is why the
   approval block alone is a `never_alone`.

**Leg 2 — recommended dimensions: DIFFERENT.** The schema's researched default is
`project → design_item → lifecycle_stage → engineering_artifact_type`. This row recommends
`project → design_item → engineering_artifact_type` — the default **minus `lifecycle_stage`** — and
the omission is evidential, not aesthetic. A change record's own state is a **disposition**
(submitted, approved, rejected, implemented, closed), not a product lifecycle gate. Filing it under
`lifecycle_stage` would file the change under the state of a *different object*, and that state
moves: an item advances from detailed design to qualification while an approved change's meaning
does not, so the folder would migrate for a reason unrelated to the file. Two optional branches are
recorded: a register drops the `design_item` level entirely (its rows span many items, and picking
the most frequent would be a fabricated fact), and a programme-organised corpus may keep `project`
alone. `time_first: false` — this material is item-primary, and dating a change trail scatters one
item's history across years.

The change identifier is deliberately **not** a level. A directory per ECO number produces one-file
folders and scatters exactly the trail the row exists to assemble.

**Leg 3 — privacy: DIFFERENT IN KIND, argued as inference.** Every engineering artifact is
proprietary, so "more sensitive" would be a degree claim and would not earn a node on its own. The
difference in kind: this is the one engineering artifact that routinely states **what was wrong**. A
reason-for-change field naming a field failure, a safety defect, a warranty trend or a supplier
dispute is an admission bound to an identified item and named approvers. The drawing shows the
part; the change order says why the old part was replaced. Marked `inference` — `00` supplies the
binding rule that privacy is enforced before any model or connector receives content; it does not
name engineering change records.

---

## The collision fixture

**`LOT-24-081_NCR-0442_Bushing-Cracking.pdf`** — a nonconformance report. It carries an affected
part number (`BPA-210`, the *same item* as this row's headline fixture), a disposition slot reading
`rework`, an approval roster, a reason describing a physical failure, and a quantity. That is four
of this row's signals on one page, on a matching part number, in the same programme folder. It is
the file most likely to be mis-filed here, and matching part numbers make it worse, not better.

**What discriminates it: the object of the disposition.** A nonconformance dispositions *one
produced quantity* — a lot, a serial range, material physically on hand — and dies with that
material. This row's change alters the *released definition* and applies to all future units. The
observable consequences: the NCR has a `Lot` slot and a `Quantity Affected` slot and **no revision
pair**; the ECO has a from/to revision pair and an **effectivity** and no lot. Reciprocally: when
an NCR proposes a design change, that proposal is a *separate ECR file*, and the two are group
members joined by a link — never one file with two homes. Named on both sides in `collides_with`.

Secondary collision, kept because it is subtler: **`PCN-2026-0331_Supplier-Bushing-EOL.pdf`**, a
supplier's product-change notification. It has a from/to part number pair, a change identifier and a
date — and it is not this row's, because the issuer is the supplier and the object is *their*
product. The recipient's decision is not on the page. Issuer role decides.

---

## Reciprocal boundaries

Every one names the same fixture on both sides.

| Neighbour | Their side | This row's side |
|---|---|---|
| `construction_property.variation-claim` | `VO-014_Level-2-Cladding-Instruction.pdf` — a site, a contract clause, an instruction role. Their landed row already names this id and this discriminator; I reciprocated rather than restating it. | `ECO-1187_…_RevC-to-RevD.pdf` — an item identifier, a revision pair, a specification. Both files are numbered, priced, time-affecting and approved, so the change structure discriminates nothing. |
| `manufacturing.nonconformance-capa` | `LOT-24-081_NCR-0442…pdf` — disposition of one produced quantity. | The same part number on `ECO-1187…pdf` — disposition of the definition. Revision pair + effectivity vs lot + quantity. |
| `business_operations.contract-administration` | `CO-07_Statement-of-Work-Amendment.pdf` — amends price, scope, dates; two signatures; no item, no revision, no effectivity. | An ECO carrying a cost-impact page is still this row's: the cost is an *impact of* a definition change, not an amendment to an obligation. |
| `engineering.drawing-package` | The released `BPA-210-001_Brake-Pedal-Assembly_RevD.dwg` that the change produced. | `BPA-210-001_RevD_redline.pdf` — clouded, triangled, stamped with a change identifier. Same event, two files, two homes. A revision block on a released sheet is the *result* of a change and never this row's evidence. |
| `engineering.bill-of-materials` | A product-structure table: parent/child composition, quantities, design-authoritative. | An affected-documents table: each row asserts an artifact must be reissued under one change identifier; no quantities. Same grid shape, opposite claim. |
| `business_operations.meeting-record` | `CCB_2026-05-12_Minutes.docx` read as attendance + agenda + actions. | The same file read as dispositions bound to change identifiers. This one is genuinely both, and is the row's single `also_holds_with` fixture. |
| `code.software-project` | A PR titled `change bushing material config` — identifier, from/to diff, review roster, approval. | The schema anchor's own node test governs: revision control alone is shared with code and never activates engineering by itself. A physical or system configuration item outside the repository is required. |
| `manufacturing.supplier-qualification` | `PCN-2026-0331…pdf` — inbound correspondence about the supplier's product. | The internal ECR the PCN triggers is a separate file and is this row's. |

---

## Files considered and rejected

- **A drawing's revision-history block** (`BPA-210-001 … Rev A/B/C/D` table in a title block).
  Tempting: it is literally a list of changes with dates and approvers. Rejected: it is *part of the
  drawing*, not a record about a change. It is evidence that changes happened; the change record is
  the file that decided one. Belongs to `engineering.drawing-package`.
- **`CHANGELOG.md`.** A change-word file with versions and dates. Rejected: repository artifact,
  `code.software-project`, and the anchor's revision-control rule kills it outright.
- **A PLM export listing every object's revision state.** Rejected: a system dump, not a record. Its
  rows are states, not decisions; nothing on it is dispositioned.
- **A calendar invite `CCB Weekly`.** Rejected as a file example, kept as a `never_alone` idea. It
  is a recurring meeting; it carries no change identifier and no item, and firing on it would file
  the whole series.
- **A supplier quotation for the new bushing.** Rejected as a file example: it is procurement
  evidence that happens to sit inside `ECO-1187_Package.zip` as a manifest member. It is a group
  member, not this row's activation evidence — which is exactly why the archive fixture reads its
  manifest without extracting members.
- **A recall notice.** Tempting (a change with a reason and an affected item). Rejected: its object
  is fielded units and its audience is customers or a regulator; it is a compliance/notice record.
  Routes to `Independent Records` unless an internal change file exists beside it.
- **A `.dwg` whose filename contains `ECO`.** Rejected on the extension and folder-name
  `never_alone` rules — `00`: *treat the file extension as a routing signal rather than an
  assumption about meaning*.
- **`Change Request Form.docx` (blank).** Not rejected — **kept**, as the row's sharpest
  `never_alone` fixture. It carries *every slot this row keys on* and none of the values, sits
  beside two filled requests, and the correct outcome is that nothing activates. It is marked
  `group_without_copying_facts: true` and routes to `Review Later`.

## Sparse-file discipline

Two fixtures carry `group_without_copying_facts: true`. The blank form may sit in the change
neighbourhood without acquiring a design item, a change identifier or a disposition from its
neighbours. `IMG_4471.HEIC` — a photograph of a redlined print on a whiteboard — carries only the
universals plus `media_type`, and its `must_not_conclude` quotes `00` directly: *the system must
not mistake the absence of EXIF for proof that an image is a screenshot*. Both are the `HW 3.pdf`
case: the neighbourhood is the only thing suggesting a domain, and the graph assembles context
without propagating labels.

## `proposed_fields` — empty, deliberately

`fields: []` by PR-6 and by rule 12 (a template never copies its schema's list). `proposed_fields`
is also empty, and that is the considered decision rather than an omission.

The one key this material genuinely tempts is a **change identifier**. It is not proposed. It is a
record identifier, and the moment it becomes a field the next question is whether it may be a
folder level — where the answer is no, because a directory per change number yields one-file
folders and scatters the very trail this row exists to assemble. Its job is retrieval and
link-following, not destination. Recorded as NJ-ECO-1 for R1c instead of minted.

The from/to revision pair reuses the schema row's existing `revision_or_baseline` proposal rather
than minting a variant, per the brief's reuse rule. Twelve `proposed_context_terms` are offered for
R6, marked PROPOSED — `00` states the pattern-plus-context shape for course codes only and does not
list these.

`role_split` is empty and the refusal is argued in the JSON: the split this material wants is
originator vs dispositioning authority, both in labelled slots on the same page, and there is no
canonical key for either role. `authored_by` is not a destination under `00`'s authorship rule.

## Neighbours considered that did **not** get an edge

- **`engineering.requirements-specification` / `engineering.verification-validation`** — a change
  can re-baseline a requirement and force a re-test, but the discriminating evidence never
  competes: a requirements document has requirement rows and verification methods, not a from/to
  revision pair on an item. `business_operations.product-requirements` already collides with both;
  adding a third claimant would give one evidence item three homes.
- **`engineering.stage-gate-review`** — genuinely close, and rejected on the leg-2 argument: a gate
  review is *about* lifecycle stage, which is precisely the dimension this row drops. If anything,
  the two rows are complementary evidence that `lifecycle_stage` belongs there and not here.
- **`manufacturing.production-record`** — reached only through the effectivity slot. The
  `manufacturing` co-activation already carries that relation at schema level; a template-to-template
  edge would double-count it.
- **`manufacturing.work-instruction`** — appears as a *row in the affected-documents table*, which
  is a link, not a collision. Naming it as an edge would encourage exactly the fact-transfer the
  grouping rules forbid.
- **`engineering.invention-disclosure`** — a change and a disclosure both describe a technical
  novelty, but a disclosure's object is a claim to ownership and it has no affected released item.
- **`research.*`** — no shared discriminating evidence; a change record's object is a designed item
  under control, never generalizable knowledge.

## Audits run before returning

- `python3 -m json.tool` — parses.
- All five `00` spans matched **verbatim** against the source: the Independent Records, Review
  Later and Unsupported or Encrypted sentences (line 120), the EXIF sentence (line 32) and the
  extension clause (line 35). No `00` quotation in this node is fabricated or paraphrased.
- `source_type` in `SOURCE_TYPES` 13/13; `collides_with.domain` a roster id 8/8; both
  `also_holds_with` domains are roster schema ids and both appear on the engineering schema row's
  own `also_holds_with`; `falls_through_to` and every `falls_through_if_inactive` is a §7.3
  residual name.
- `fields` and `proposed_fields` empty, each with a note. No threshold, score, evidence count or
  handling class; `sensitivity` is `potentially_sensitive` only.
- Only the two assigned files were written. No roster, canonical-fields, `check.py`, `src/`, SPEC
  or neighbour node was touched.

## NEEDS-JOSEPH (this node only)

- **NJ-ECO-1 — the change identifier has no key, and this row refuses to mint one.** Three answers:
  (a) it stays search-and-link metadata, which is what the row recommends and what its dimension
  order encodes; (b) a `record_identifier`-style key is minted on the shared vocabulary, which
  immediately raises whether it may be a folder level — this row's answer is no; (c) it is folded
  into the schema's `revision_or_baseline`, which would overload that key with two different
  meanings (a state of an artifact, and a transaction over artifacts). **Recorded, not resolved.**
- **NJ-ECO-2 — who owns a nonconformance that proposes a design change, when it is one PDF and not
  two.** The row assumes the common case (NCR and ECR are separate files, joined as group members).
  Where a single document does both, the alternatives are: route on the *disposition's object*
  (this row's preference — if a revision pair and an effectivity are present, engineering; if only a
  lot and a quantity, manufacturing), or declare a genuine `also_holds_with` at template level.
  Deciding this unilaterally would have quietly widened the schema's edges.
- **NJ-ECO-3 — does a deviation or waiver belong on this row at all?** `Deviation-Permit-0087…pdf`
  permits a bounded departure and explicitly *does not supersede* the definition — it fails this
  row's single sharpest signal, the from/to revision pair. It is kept here because it is
  dispositioned by the same board on the same item with the same approval structure, and because
  `engineering.change-order` is the only roster row that could plausibly hold it. The alternatives:
  keep it (today's answer), or route deviations to `Review Later` and surface a roster gap to R1c.
  This is the one place where the row is holding coverage on adjacency rather than on its own
  discriminating structure, and it is stated rather than smoothed.
