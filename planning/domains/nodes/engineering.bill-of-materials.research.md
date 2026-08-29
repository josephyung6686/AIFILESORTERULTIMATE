# engineering.bill-of-materials — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.bill-of-materials.json`](engineering.bill-of-materials.json).
Salvage: none — no prior draft existed for this id.

**Verdict: `refuse_node: true`.** The row's name is item eight of its own schema's `work_types[]`
enum. Its only candidate detection signal is deterministic signal five on that same schema. Its
dimensions and its privacy rule are the schema's, unchanged. The coverage is not lost — it is
already recognised by `engineering`, and the seven boundaries this row was reaching for are
recorded reciprocally for R1c.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — the standing brief, in full.
- `python3 planning/domains/dispatch/make_prompt.py engineering.bill-of-materials` — the stamped
  assignment: `must_consider_neighbors` = manufacturing, code, research; `must_consider_residuals`
  = Independent Records, Review Later; `inherited_field_keys` = [] (PR-6).
- `planning/domains/nodes/engineering.json` — **the schema anchor and the decisive evidence.**
  Read for `node_test`, `proposed_fields`, `recognition`, `work_types`, `grouping_reasons`,
  `template`, `file_kinds`, all five collisions, `also_holds_with`, `falls_through_to`,
  `sensitivity_why`, `open_question`. Every string this memo attributes to the anchor was pulled
  from that file mechanically, not remembered.
- `planning/00-database-agent-product-design.md` — grepped, never streamed. Lines 37, 47, 57, 70,
  95, 99 and 120 supplied every `00` quotation used here and in the JSON.
- `planning/domains/CONNECTION.md` §2 — the node test, read verbatim (lines 75–100), plus the
  Value / Group / Residual rows of its object table.
- `planning/domains/roster.json` — every edge endpoint confirmed against `nodes[].domain_id`
  (358 rows). This is also where the sub-roster problem in NJ-BOM-1 became visible.
- `planning/domains/nodes/finance.crypto-assets.research.md` — depth calibration, per the brief.
- `planning/domains/nodes/business_operations.organisational-records.json` — the named refusal
  exemplar; read for key set and for the shape of a refusal that closes its own resurrection
  route. That last move is copied here deliberately.
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — as reproduced in the stamped prompt; every
  `file_examples.source_type` checked against the fourteen names.

One grep for landed rows already arguing a boundary against me
(`grep -rl "engineering.bill-of-materials" planning/domains/nodes/`) returned **nothing**. No
neighbour has named this id yet, so every boundary below is stated first from this side and is
owed a reciprocal from the other.

## THE CHARGE — the strongest case that this row should not exist

Constructed before anything was written, as the brief requires. It is not one case; it is five,
and each is independently fatal.

1. **It is a `work_type` value.** `engineering.json`'s `work_types[]` contains, verbatim, the
   string `bill of materials`, at position eight of eighteen. The stamped prompt's own heading is
   "Work types are values" and it forbids a child node per work type. The schema declared this
   row's name to be a value before this agent was dispatched.
2. **It is a document type.** "Bill of materials" is a document-type word, and it is the *least*
   discriminating word in this world: procurement, costing, production, service and software all
   name a different object with it.
3. **It is a file format.** The one place `bom` is a labelled, machine-readable, deterministic
   slot is a CycloneDX or SPDX software bill of materials. A format is not a node.
4. **It is defined by the absence of something.** The only clause separating this material from
   manufacturing is the anchor's own "design-authoritative rather than a production pick list" —
   a negation of a neighbour.
5. **It is a duplicate of its own schema's default template.** All three legs, below.

I could not defeat any of the five. The row is refused.

## The node test, argued in full

CONNECTION.md §2, verbatim: "A **template** row exists only if its detection signals,
recommended dimensions, or privacy rules differ from its schema's default template. ALIGNMENT: a
template that would only repeat its schema's fields and dimension order **is not a node** — it is
the schema's default template."

### Leg 1 — detection signals. Not merely similar: the same bullet.

The only discriminator this material has is a parent-child product-structure table with
quantities and drawing/revision references. `engineering.json` already declares exactly that as
deterministic signal five:

> a BOM or product-structure table with a parent assembly identifier, child item/part
> identifiers, quantities and drawing/revision references, where the table is design-authoritative
> rather than a production pick list

Its ambiguity surface is declared too — `needs_llm` two ("whether a spreadsheet headed BOM is the
authoritative design product structure, a manufacturing pick list, a procurement list, or a
costing sheet") and `never_alone` six ("a table called BOM alone; procurement, costing, production
and spare-parts records use the same label"). A template whose signal is one line of its own
schema's default deterministic list has nothing of its own to fire on, and writing it would put
two claimants on one evidence structure.

The honest counter-argument, and why it fails: this row could *elaborate* the signal — level and
find-number columns, quantity-per, unit of measure, make-or-buy, reference designators. But
elaboration is not difference. Every one of those is a column of the structure the schema already
names, and the node test asks whether the signals **differ**, not whether they can be described
at greater length. Elaboration belongs in R2's pattern work, which this row may not do anyway.

### Leg 2 — recommended dimensions. Identical, and structurally so.

The anchor's researched conditional order is `project → design_item → lifecycle_stage →
engineering_artifact_type`. `bill of materials` is one **value** of that final dimension. A row
named after a value of its own schema's leaf dimension is that dimension's leaf folder wearing a
roster id.

`00` is explicit about what a value is (line 37, verified):

> A fact is a statement such as subject = BUSIB 4300, term = Spring 2026, work type = syllabus,
> capture date = 2026-07-17, or purpose = university application.

and about what a field is (line 47, verified):

> Academic files may use school, term, course, instructor, and work type.

Work type is the field; `syllabus` is the value. Here `engineering_artifact_type` is the field and
`bill of materials` is the value. `00`'s tree-design warning names the exact defect this row would
create (line 99, verified):

> It should warn when a level produces only one child, repeats a concept already expressed in the
> parent, creates excessive depth, or creates a large number of tiny folders.

And separately, under binding PR-6, `engineering` declares no field rows, so `dimension_order` is
`[]` on the schema and must be `[]` on every template of it. There is not even an expressible
difference to argue. That mechanical fact does not carry the refusal by itself — a template could
still survive on leg 1 alone — but it removes any route to surviving on leg 2.

### Leg 3 — privacy rules. Identical, and the vocabulary cannot express a difference.

The anchor is `potentially_sensitive` because engineering packages carry "proprietary design
definition, supplier data, vulnerabilities, safety analyses, export-controlled or critical-technology
information, signatures and test evidence." A BOM's supplier column and unit-cost column are
instances of that same sentence, not a new rule. Sensitivity here is only
`none | potentially_sensitive`, and handling classes are P7's, so there is no vocabulary in which
this row could state a different rule even if one existed.

Three legs, three failures. Refuse.

## The resurrection route, and why it is closed

The strongest revival argument — the one a later agent will actually make — is that a
parent-child-with-quantity table is a **relation between two labelled roles**, not a never-alone
token, and that this is the same move that legitimately saved a holder/subject row in another
domain. Four answers, any one sufficient. All four are written into `refuse_reason` so the JSON
defends itself without this memo.

1. **The relation is not co-extensive with the row.** A CAD assembly tree, a drawing's associated
   parts list and a change order's affected-items list all carry the identical relation. So the
   relation individuates *engineering against manufacturing* — which the schema already does in
   its `manufacturing` collision — and does not individuate this row against its own siblings.
2. **Both roles are the same entity type.** Parent assembly and child part are `design_item` at
   two depths of one tree. The closed vocabulary's instrument for one entity type in two roles is
   `role_split`, which must point at a **neighbour** holding the other role. There is no such
   neighbour: both roles live inside engineering. `role_split` is therefore `[]`, and it is empty
   for a reason, not by omission.
3. **The rows that survive a two-role argument survive because the relation changes the privacy
   rule.** Here privacy is unchanged (leg 3), so the leg that carried them is missing.
4. **The relation is already the schema's own declared signal.** Evidence a schema declares for
   itself cannot be a child row's distinguishing evidence.

## Files considered and rejected

Eleven fixtures are in the JSON. What they are there to prove is that the id is a label: on every
one of them the correct outcome is either the **schema** firing without this row, or a neighbour,
or a residual.

| Fixture | Why it is in the list |
|---|---|
| `BPA-210_BOM_RevC.xlsx` | the happy case — and it activates `engineering` on the schema's own signal five, with nothing left for this row to add |
| `bom.json` (CycloneDX) | **the collision fixture**; the filename is literally the row's name |
| `LOT-24-081_pick_list.csv` | same columns, flat, plus lot/bin/issued — the execution twin |
| `Spare Parts List - Model 40 Compressor.pdf` | carries the parent-child-quantity relation in full and is still not this row's evidence |
| `Assembly Drawing A-2201 sheet 2 - parts list.pdf` | the same table drawn inside a title-block frame — a sibling's bytes |
| `ECO-1187_affected_items.xlsx` | from-rev/to-rev + disposition; the change is the object, not the structure |
| `BPA-210.asm` | the product structure as a model rather than a list |
| `Costed_BOM_Q3_margin.xlsx` | the word in the filename, a margin rollup in the columns |
| `RE: BOM sign-off for BPA-210 Rev C.eml` | subject-line-only evidence: a type word, a part-number shape, a revision token — three never-alones stacked |
| `Screenshot 2026-03-04 at 11.02.14.png` | the sparse `HW 3.pdf` case, cropped above the identifying header |
| `bom_export.zip` | the mixed archive packet, manifest read without extraction |

Rejected from the kept corpus, with reasons:

- **A purchase order / RFQ line-item schedule.** Real, and it looks like a BOM. It is a
  transactional record whose discriminating slots are a vendor, a PO number and prices; it belongs
  to a finance or procurement claimant, and admitting it would have made this row a purchasing
  domain by the back door.
- **An `npm ls` / `pip freeze` text dump.** A dependency list with no format declaration. It is
  repository evidence; kept out because the CycloneDX fixture already teaches the discrimination
  with a *labelled* slot, which is the harder and more useful case.
- **A PCB pick-and-place / centroid file.** Parent-child-ish, quantity-ish, and genuinely
  engineering-adjacent — but its discriminating content is X/Y/rotation placement data, which is
  manufacturing execution input. It belongs beside `engineering.pcb-layout`'s own boundary, and
  taking it here would have been this row stealing a sibling's problem.
- **An IFC / construction schedule of quantities.** A bill of quantities is a genuine near-homonym
  ("BOQ"), and it is site-bound and contract-scoped. It is `construction_property`'s, on the seam
  the anchor already draws; NJ-ENG-3 on the anchor covers it and this row must not pre-empt that.
- **A recipe or ingredient list.** The parent-child-quantity structure is present and the domain
  is not. Left out because it teaches nothing about the engineering seam and would have padded.
- **A restaurant or retail inventory sheet.** Same reason.
- **A `manifest.json` in an app bundle.** A format with a component list; no product structure and
  no physical item. `code`'s.

## `proposed_fields` — empty, and the two temptations named

`proposed_fields: []`. Two keys were genuinely tempting and both were rejected on the spot:

- **`quantity_per`.** It is a *cell value inside a table*, not a fact about the file. No file is
  "a quantity of 4". Minting it would put a table column into the field vocabulary, which is the
  move that produced thousands of private field names in the overnight pass.
- **`parent_item`.** This is `design_item` at a different tree depth — the same key, not a new
  one. Under §3.8's rule that a role split is the *only* licence for a near-duplicate field, a
  split needs two different roles held by two different rows; here one row holds both. Rejected.

`fields: []` by contract (a template never copies its schema's list, and PR-6 leaves the schema
with none anyway). `proposed_context_terms: []` — this row proposes no term list, because the
disambiguation it would need (`design-authoritative` versus `pick list`) is a judgement, not a
vocabulary, and the anchor already routes it to `needs_llm`.

## Reciprocal boundaries — both directions, same fixture bytes on both sides

Recorded in `collides_with` on a **refused** row deliberately: the boundaries are real and belong
to the `engineering` schema, and R1c needs them written down somewhere when this id is struck.
None of them is reciprocated yet — the grep found no landed row naming this id — so each is owed
a matching sentence from the other side, which this agent may not write.

| Neighbour | Fixture bytes named on both sides | Boundary |
|---|---|---|
| `manufacturing.production-planning` | `LOT-24-081_pick_list.csv` | flat + lot/bin/issued ⇒ manufacturing, even citing Rev C · level column + qty-per + drawing refs, no lot/bin ⇒ engineering, even listing the same parts |
| `manufacturing.spare-parts` | `Spare Parts List - Model 40 Compressor.pdf` | recommended-stock + order-code, addressed to a technician ⇒ manufacturing · controlling revision block + approval slot ⇒ engineering, even though it enumerates orderable parts |
| `code.software-project` | `bom.json` | `bomFormat`/`specVersion` + purl coordinates at a repo root ⇒ code · drawing refs + revision block ⇒ engineering, even when exported as JSON or XML |
| `engineering.drawing-package` | `Assembly Drawing A-2201 sheet 2 - parts list.pdf` | title block is the discriminator, so the sheet is one artifact · a standalone sheet with no title block or approval is not a drawing package even citing drawing numbers |
| `engineering.change-order` | `ECO-1187_affected_items.xlsx` | from/to revision + disposition ⇒ the change is the object · a single stated revision, no from/to ⇒ the definition, not the change |
| `engineering.cad-model` | `BPA-210.asm` | internal tree ⇒ a model, instance counts are not qty-per · a tabulated export of that tree ⇒ a list, not a model |
| `business_operations.project-delivery` | `Costed_BOM_Q3_margin.xlsx` | cost/margin columns, no revision or approval ⇒ business_operations · the same rows with a controlling revision block ⇒ technical definition |

The last four are **same-schema** collisions between values of one `engineering_artifact_type`
field. That they exist at all — that four roster rows fight over which value a table is — is the
clearest symptom of NJ-BOM-1 below.

## The collision fixture

`bom.json`, a CycloneDX software bill of materials at a repository root. It is the sharpest
possible false positive because the row's exact name is a **labelled JSON key**, not an inferred
filename token — this is normally the strongest evidence class the product has, and here it is
worthless. What discriminates it: `bomFormat`/`specVersion` declare a software-inventory format;
`components[]` members carry package-URL coordinates, versions and licence identifiers; there is
no drawing number, no revision block, no physical part identifier and no quantity-per. It is
`code.software-project`'s. Where an SBOM is *also* a released component of a physical baseline,
that dual claim runs through `engineering.json`'s existing schema-level `also_holds_with` with
`code` — never through this row.

`also_holds_with` on this row is `[]`, and that is contract, not oversight: `_CONTRACT` rule 14
restricts `also_holds_with` to **schema** rows. A template widening its schema's co-activation set
is exactly the seam where a template quietly outgrows its schema.

## Neighbours considered that did **not** get an edge

- **`research`** (a `must_consider_neighbors` entry, so it is answered explicitly). The anchor's
  research overlap is models, experiments, prototypes and validation language — artifacts whose
  object is knowledge. A product structure has no experimental object and produces no
  generalizable claim; a materials list in a lab notebook is a reagent inventory, which is
  `research.lab-notebook-protocols`' evidence and shares no discriminating slot with a
  parent-child assembly tree. No shared evidence, therefore no edge. Asserting one would have been
  padding.
- **`manufacturing` (the schema)** — the collisions are with the two specific rows that hold the
  competing fixtures. Adding the schema too would give one evidence item two claimants on the same
  side.
- **`construction_property.*`** — a bill of quantities is a genuine homonym, but it is site-bound
  and the seam is already the anchor's, with NJ-ENG-3 open on it. Deliberately not pre-empted.
- **`engineering.material-specification`** — tempting, since a BOM's child rows cite specs. But a
  specification is a *document a BOM row points at*, not a competing reading of the same bytes.
  A citation is not a collision.
- **`role_split`** — empty, and this is the interesting refusal, argued in full above: the two
  roles are the same key.

## Sparse-file discipline

Two fixtures carry `group_without_copying_facts: true`. `Screenshot 2026-03-04 at 11.02.14.png`
is this node's `HW 3.pdf`: an indented list with quantities, cropped above the identifying header,
sitting beside two real BOM exports. It may join their neighbourhood and must receive nothing from
them — `00`, verified at line 57: "Its output does not directly create a course fact on HW 3.pdf".
`RE: BOM sign-off for BPA-210 Rev C.eml` is the second: its entire candidate evidence is three
stacked never-alone tokens in a subject line.

## Audits run before returning

- `python3 -m json.tool` — parses.
- Every `00` span in quote marks in both files re-grepped verbatim against
  `planning/00-database-agent-product-design.md` before writing: the three residual definitions
  (line 120), the fact-statement sentence (line 37), the academic-fields sentence (line 47), the
  tree-warning sentence (line 99), the reverse/remove/add/flatten clause (line 95), and the
  HW 3 clause (line 57). No `00` quotation here is fabricated or paraphrased inside quote marks.
  Spans attributed to `engineering.json` and `CONNECTION.md` are marked as such and were pulled
  mechanically from those files, not from memory.
- Every `file_examples.source_type` is in `SOURCE_TYPES` (11/11).
- Every `collides_with.domain` resolves to a `roster.json` `domain_id` (7/7). Every
  `falls_through_to.residual_template` is one of `00`'s nine names (3/3).
- `fields`, `proposed_fields`, `work_types`, `proposed_context_terms`, `also_holds_with`,
  `role_split` and `template.dimension_order` are all empty **by argument or by contract**, each
  with the reason stated in the file itself.
- No threshold, score, count of evidence or handling class appears. `sensitivity` is
  `potentially_sensitive` only.
- Only the two assigned files were written. `planning/29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `engineering.json`, `check.py`, `src/` and every neighbour node were
  read at most, never modified.

## NEEDS-JOSEPH (this node only)

- **NJ-BOM-1 — the `engineering.*` sub-roster is one node per work-type value, and this refusal
  generalises.** `cad-model`, `drawing-package`, `electrical-schematic`, `pcb-layout`,
  `change-order`, `material-specification`, `risk-analysis-fmea`, `prototype-build`,
  `verification-validation` and `simulation-analysis` are each, like `bill-of-materials`, a
  verbatim member of `engineering.json`'s `work_types[]`. Every step of the argument above applies
  to them unchanged. This must be decided **en bloc**, or the outcome will depend on which agent
  drew which id — which is not a design. Three alternatives: **(a)** refuse the value-named rows
  and keep only rows that are organizational *situations* with genuinely different signals,
  dimensions or privacy — `commissioning-handover`, `aerospace-airworthiness` and
  `standards-library` look like the plausible survivors, on regulatory or lifecycle evidence
  rather than artifact type; **(b)** keep them browse-only as the value list that populates
  `engineering_artifact_type`, which is a P6 values table and not a roster; **(c)** redefine each
  as a situation rather than an artifact type — real work, and not this row's to do for its
  siblings. **Recorded, not resolved.**
- **NJ-BOM-2 — where does a CycloneDX/SPDX SBOM activate?** Recommendation: `code.software-project`
  on repository evidence, with `engineering.embedded-firmware` claiming it only when a
  released-baseline relation is independently evidenced; the dual case is already covered by
  `engineering.json`'s schema-level `also_holds_with` with `code`. A reciprocal sentence is owed on
  `code.software-project`, which this agent may not write. Confirm, or invert.
- **NJ-BOM-3 — if the coverage should survive without a node, the honest vehicle is a
  `grouping_reason`, not a template.** Recommended addition to `engineering.json`: *one parent
  item's product structure and the child part definitions, specifications and drawings it
  enumerates*, beside the existing lifecycle grouping reason. Grouping is not activation and needs
  no roster row. **This is a recommendation to R1c; `engineering.json` was not edited.**
