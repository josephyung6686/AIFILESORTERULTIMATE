# engineering.drawing-package — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.drawing-package.json`](engineering.drawing-package.json).
No prior draft existed; both files are written fresh in this pass.
Verdict: **node survives, refuse_node: false** — but only after being redefined away from what its
roster name literally says. The charge below is the most useful part of this memo.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped assignment from
  `make_prompt.py engineering.drawing-package` — the six requirements, the node test, the output
  shape, and the `one_line_hint` recording that this row absorbs the legacy id `eng.gdt-tolerance`.
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted grep only.
  Five spans are quoted in the JSON; the audit below re-matched all of them mechanically.
- `planning/domains/nodes/engineering.json` — the schema anchor this row is measured against. Its
  default order, its ten default deterministic signals, its `work_types`, its five schema-level
  collisions and its four proposed keys (`design_item`, `lifecycle_stage`,
  `engineering_artifact_type`, `revision_or_baseline` as metadata) are the baseline for every
  "differs from the default" claim made here.
- `planning/domains/nodes/finance.crypto-assets.research.md` / `.json` — the depth and idiom
  calibration named in the brief; key set, `*_note` conventions, the empty-by-contract pattern.
- `planning/domains/roster.json` (358 nodes) — every edge endpoint resolved mechanically, and the
  source of the sibling list that produced the intra-schema boundaries below.
- `planning/domains/canonical_fields.json` (37 keys) — no key minted; exactly one proposed.
- `SOURCE_TYPES` as given verbatim in the assignment — all twelve fixtures checked against it.

One grep was run for landed rows that already argued a boundary against this id
(`grep -rl "engineering.drawing-package" planning/domains/nodes/`). **It returned nothing.** No
neighbour node has yet named this row, so every boundary below is authored from this side and is
flagged in the JSON where R1c must reciprocate it — most importantly on
`construction_property.drawings-revisions`, which had not landed when this was written.

## THE CHARGE — the strongest case that this row should not exist

I put the prosecution first because on this particular id it is very strong, and three of its five
counts are correct as stated against the row's *name*. The row survives only because the name is
not what the row is.

**Count 1 — it is a work_type value.** `engineering.json`'s own `work_types[]` contains the string
`"engineering drawing"`. ALIGNMENT is explicit that work types are values of a field, never nodes.
A row called "Engineering drawings" is, on its face, one enum value of the schema's own
`engineering_artifact_type` promoted to a node. This is the exact failure the 574 is being
unwound from.

**Count 2 — it is a lifecycle attribute the design already makes universal.** "Under revision
control" describes versioning, and `00` already lists version-family membership among the facts
every file may carry, in the same breath as the syllabus example: a file may be "a member of a
version family, and potentially sensitive." Universals belong to no domain. A row whose
distinguishing adjective is a universal has no distinguishing adjective.

**Count 3 — it is a file format.** `.dwg`, `.dxf`, `.step`. Extension is a `SOURCE_TYPES` question
and `00` forbids extension as sole proof. If the row is "the CAD files", it is not a node.

**Count 4 — it duplicates neighbours.** `engineering.cad-model` already holds the drawing's source.
`engineering.change-order` already holds the revision event. `engineering.bill-of-materials`
already holds the parts table. And `construction_property.drawings-revisions` is, by its id,
*literally a drawings-and-revisions row on another schema*. What is left for this row after those
three siblings and that cousin take their share?

**Count 5, the sharpest — it duplicates its own schema's default template.** The engineering
schema's researched default order ends in `engineering_artifact_type`. A "drawings" row is that
last dimension pinned to one value. A row that is a leaf of its own schema's final dimension is
definitionally not a template: its detection signals, dimensions and privacy rules would all be
the schema's, filtered.

### Defeating the charge

Counts 1, 3 and 5 are defeated together, by the same move: **the row's evidence is not the document
type, it is a structure — the title-block slot cluster joined to a revision-history table.** That
structure is a labelled-slot relation, and it does three things no artifact-type value can do.

- It **fires where the schema default does not.** The schema's ten default deterministic signals
  all require a controlled-definition context: a requirements matrix, a TDP manifest joining
  specifications and standards to a baseline, an engineering-change structure with an affected
  item, a BOM with parent/child indenture, an analysis package comparing margins to named
  requirements, a verification matrix with requirement identifiers. A bare `.pdf` plot with a
  title block, a revision-history table, three dimensioned views and *no* requirement identifier,
  *no* project name and *no* BOM matches none of those ten. Under the schema default alone it
  goes to a residual. That is a detection difference with a fixture, not a filter.
- It **fails to fire where the type word would.** `Untitled1.dwg` is a CAD drawing by extension and
  by type word, and this row correctly does not activate on it. So the row is not the extension
  (defeats count 3) and not the type word (defeats count 1).
- It **is a relation across files, not a property of one.** Two of the seven deterministic signals
  — the sheet-set relation and the supersession mark — can only be evaluated by comparing
  extracted identifiers across files. A `work_type` value is a property of one file. This is the
  structural reason the row is a filing situation and not an enum member.

Count 2 is defeated by inverting it. The row's central recommendation *about* the version family is
a **refusal**: revision is the single best-labelled slot in this entire material and therefore the
first folder level any naive design would build, and building it is what destroys the unit. The row
exists to say "not that level" — which a universal cannot say, because a universal has no opinion
about dimension order for any particular situation. Its argument leans on `00`'s own guardrail:
"It should warn when a level produces only one child, repeats a concept already expressed in the
parent, creates excessive depth, or creates a large number of tiny folders", and on the fact that
`00` already provides the retrieval mechanism that makes the folder unnecessary — "Structural
relationships should retrieve nodes that contain a version family, duplicate family, archive
family, photo event, or derived document set."

Count 4 is defeated per neighbour, with reciprocal boundaries and shared fixture bytes; see below.
The short form: cad-model owns the authoring source, change-order owns the instrument, BOM owns
the product structure that outlives any one sheet, construction owns the site-bound series. What
remains — the issued, title-blocked, revision-controlled sheet series and its associated list — is
a real and populous residue, and it is the thing engineers actually go looking for.

**What did NOT survive the charge:** the row's roster name. "Engineering drawings under revision
control" reads as a document type plus a universal, i.e. as counts 1 and 2 conceded. The JSON's
`name` is rewritten to *Title-blocked drawing sheet series under revision control*, and the
`one_line` states the unit as a version family carrying a title block. If R1c prefers the original
name, the row should be re-examined, because the name is the version of this row that fails.

**And one absorbed id that I recommend is NOT saved:** `eng.gdt-tolerance`. Geometric dimensioning
and tolerancing is a *notation*, not a filing situation. Its evidence — a feature control frame, a
datum identifier, a general-tolerance note — is densest in published standards and inspection
reports, i.e. in two *other* rows' files. A tolerancing node's only evidence would be never-alone
evidence and it could never activate. Its coverage is discharged here as one recognition signal
plus two collisions (`manufacturing.inspection-record`, `engineering.standards-library`). Recorded
as NJ-DWG-5, a recommendation to R1c, not a decision taken here.

## The node test, all three legs

Stated in full in the JSON's `node_test_note`; the honest summary is that it passes on two legs and
the third is a refinement, and I would rather say that than pad it to three.

1. **Detection differs — yes.** Argued above with the fixture the schema default sends to a residual
   and this row keeps, and the fixture (`Untitled1.dwg`) the type word keeps and this row sends away.
2. **Dimensions differ — yes, and this is the load-bearing leg.** Schema default: `project →
   design_item → lifecycle_stage → engineering_artifact_type`. This row: `design_item →
   engineering_artifact_type`, with three named departures. `lifecycle_stage` is dropped because the
   only stage-shaped evidence here is a title-block STATUS slot holding released / in-work /
   superseded / void — a *document state* that would build a Superseded folder competing with the
   version family for the same bytes, which is `00`'s "repeats a concept already expressed in the
   parent" verbatim. `project` is demoted to optional, because a drawing identifier routinely
   outlives the programme that created it. The revision designator is refused as a level outright.
3. **Privacy differs — only in locus, and I say so.** The schema is already `potentially_sensitive`,
   so no new class is available or claimed. What is different is that distribution statements,
   export-control markings and approval signatures sit *inside the very slot cluster the row
   activates on*, so a marking read there scopes to the whole sheet series rather than the one
   stamped file. **The row would still stand if this leg were struck**, which is why it is not
   leaned on.

`fields: []` and `template.dimension_order: []` — both empty because PR-6 leaves the engineering
schema with no declared fields and a template may only branch on a field its own schema declares.
Encoding levels now would make this row the place where a proposed key silently became legal. The
conditional order is written in `template.why` instead, exactly as the schema anchor does.

## Reciprocal boundaries — each with the same fixture bytes on both sides

Eight collisions, none of them decorative. The four that matter most:

| Neighbour | Shared fixture | This row owns | The neighbour owns |
|---|---|---|---|
| `engineering.cad-model` | `BPA-210-002.dwg` beside `BPA-210-002_RevC_..._sheet1of2.pdf` | the issued title-blocked sheet and its revision trail | the authoring source and its model-tree evidence |
| `construction_property.drawings-revisions` | `A-101_Rev_P3_Ground-Floor-Plan.pdf` | a series controlling an identified reusable design item | a series issued against one site under a contract |
| `manufacturing.inspection-record` | `FAI-Report_BPA-210-002_RevC_ballooned.pdf` | the sheet that DEFINES the tolerance | the record that MEASURES against it |
| `engineering.electrical-schematic` | `SCH_MainBoard_RevB.pdf`, `hardware/mainboard.kicad_sch` | unresolved — see NJ-DWG-2 | unresolved — see NJ-DWG-2 |

The direction each edge is most likely to be got *wrong* is stated on the edge itself, because
that is the half a one-sided memo omits: the model must never inherit `REV C` from the PDF (a
matching filename stem is a grouping relation, never a fact transfer); the ECO must never be pulled
into the drawing's version family (it is the authority that caused a member, not a member); and
*this row* is the likely thief of the FAI report, because the embedded ballooned sheet is the
larger part of that file by page count.

`construction_property.drawings-revisions` deserves a note beyond the table. It is the collision
that nearly killed the row, because a title block is genuinely the same artifact in both worlds:
same drawing-number slot, same revision slot, same sheet pagination, same scale, same
drawn/checked grid. The discriminator is not in the block's *structure* but in two of its
*contents* — a site address and a contract number present, an item identifier and an associated
list absent. Neither side may claim a sheet on the presence of a title block, a revision letter or
a scale. That edge is authored from this side only and R1c must reciprocate it.

## The collision fixture

`A-101_Rev_P3_Ground-Floor-Plan.pdf` is the designated collision fixture and it is designated
precisely because it defeats the row's *primary* signal completely. Every slot in the title-block
cluster is present and labelled. What discriminates it: the block also carries a site address and a
contract number, the drawing frame holds a floor plan of one premises with room names and a door
schedule, and there is no item or assembly identifier recurring on any parts list. Correct outcome:
`construction_property.drawings-revisions`; residual if that does not fire: `Review Later`, because
the item-versus-site question is one this row genuinely cannot settle from one file's own evidence.

The runner-up collision fixture is `Drawing standards - ASME Y14.5-2018.pdf`, and it is the one
that matters for the absorbed legacy coverage: hundreds of pages saturated with feature control
frames, datum identifiers and tolerance callouts — the densest GD&T evidence any file in this world
will ever carry — and it is not a drawing at all. Discriminator: no title block on any page, no
revision-history table, and no controlled identifier belonging to anything the user designs.

## Files considered and rejected

Beyond the twelve kept fixtures, these were considered as file examples and cut, each for a stated
reason rather than for space:

- **A `.step` / `.iges` exchange file sent to a supplier.** Looks like this row because its
  filename carries the controlled identifier. Cut because it teaches nothing `BPA-210-002.dwg` does
  not already teach — an opaque container whose stem is a grouping relation and not a fact.
- **A `.stl` sent to a 3D printer.** A mesh export with no title block and no revision authority; a
  derived artifact of the model. Including it would have widened this row toward "anything with a
  part number in the filename".
- **A drawing register / index spreadsheet.** Tempting — it lists every identifier and every current
  revision, and it is the most useful file in a real drawing office. Cut because it is the same
  shape as the transmittal already in the list: evidence about a set, donating no identifier to
  itself.
- **A markup / redline PDF with cloud bubbles and comment stamps.** Cut because it sits on an
  unresolved seam — arguably a version-family member, arguably a review artifact, arguably
  `business_operations` governance evidence. Rather than invent a rule I cannot evidence, the
  ambiguity is carried by the `needs_llm` line about marked-up working prints.
- **A CAD licence file, a `.ctb` plot-style table, a template `.dwt`.** Tool configuration, not
  evidence about a designed item. `Unsupported or Encrypted` handles them without this row.
- **A supplier's datasheet for a purchased component.** The schema anchor already routes standalone
  datasheets to `Independent Records`, and a datasheet has no controlled identifier of the user's own.
- **A calendar invite for a drawing review.** A `SOURCE_TYPE` and an event; nothing here would fire
  on it that the schema default would not.

## `proposed_fields` — exactly one, and proposed as a non-dimension

`drawing_number` only. The argument for it is that the schema's proposed `design_item` names a
*thing* and a drawing number names a *controlled document about* that thing, and the two are not in
bijection in either direction: one item carries detail, assembly and installation drawings under
three numbers, and one tabulated number covers a family of items. No canonical key holds a
controlled-document identifier (`record_type` is finance's category word, `artifact_type` is
research/code's role word, `version_family` is a relation and not an identifier, `repository` is a
code container). It is the string that anchors the version family — the thing that says these
eleven PDFs are one document at eleven states.

Two disciplines applied to it. **It is proposed `destination_eligible: false`**, against the row's
own convenience: a level per drawing number would produce one child for most items in a small
team's corpus and would repeat the item concept above it, which is two of `00`'s four warning
conditions at once. Its work is grouping and retrieval, not a directory. And **the alternative is
stated rather than hidden** — folding it into `design_item` is coherent and cheaper and is written
into the proposal itself as the option R1c may prefer.

**Nothing else is proposed.** In particular `revision` is **not** proposed, because the engineering
schema already proposes `revision_or_baseline`; proposing a variant spelling for the same role is
the failure mode the shared vocabulary exists to prevent. Thirteen `proposed_context_terms` are
listed for R6 and marked PROPOSED, not design — two of them (`superseded`, `issued for
construction`) are there because their correct effect is to move a file *away* from this row.

## Neighbours considered that did NOT get an edge

- **`research`** — a `must_consider` neighbour, and it gets no template-level edge. A lab apparatus
  drawing is real, but the evidence does not collide: research artifacts carry project, stage, lab
  and venue evidence and essentially never a revision-history table under a controlled identifier.
  The schema-level collision on `engineering.json` already covers the model/prototype overlap;
  duplicating it here would give one evidence item three claimants.
- **`business_operations.project-delivery`** — the anchor's own collision fixture is a project
  status report, which shares no slot with a title block.
- **`engineering.requirements-specification`, `.verification-validation`, `.simulation-analysis`** —
  genuine siblings, but each keys on a structure this row does not have (requirement identifiers,
  verification methods, margin comparisons). They compete with the *schema default*, not this row.
- **`also_holds_with`: empty by contract** (schema-to-schema only). One fixture claims per-file
  co-activation — `hardware/mainboard.kicad_sch` with `code`. The ballooned inspection report and
  the site plan carry `also_schema: null` deliberately: a co-activation claim and a collision claim
  on the same bytes are contradictory.
- **`role_split`: empty, deliberately.** Two tempting splits, both declined. The design office that
  owns a sheet versus the customer whose part identifier sits in the same title block — canonical
  `our_firm` / `client` exist but the engineering schema declares neither, and minting a
  design-authority key to solve one template's title block is the move that produced thousands of
  private field names in the overnight pass. And drawing identifier versus item identifier, a real
  same-entity/different-key candidate, declined because both candidate keys are still proposals and
  a split between two unadjudicated proposals is not this row's decision. Raised as NJ-DWG-1.

## Sparse-file discipline

Three fixtures carry `group_without_copying_facts: true`, and they are the row's whole thesis in
miniature. `BPA-210-002.dwg` may sit in the sheet series' neighbourhood and must acquire **no**
facts from the PDF's title block — the native model is routinely ahead of or behind the released
plot, and copying `REV C` onto it is precisely how an in-work model comes to look released.
`IMG_4471.jpg` recovers one legible title-block slot from a photographed print and gets universals
only. The transmittal mail names six identifiers and receives none of them, because a transmittal
belongs to a set and to none of its members.

## Audits run before returning

- `python3 -m json.tool` parses; 33 top-level keys, matching the landed launch-row key set plus the
  `*_note` keys and `proposed_context_terms`.
- All 12 `file_examples.source_type` and all 10 `file_kinds.source_types` are in `SOURCE_TYPES`.
- All 8 `collides_with.domain` values resolve to roster ids (checked against `roster.json`'s 358
  nodes). No id was invented.
- All 5 `falls_through_to.residual_template` names and all 12 `falls_through_if_inactive` values are
  among `00`'s nine residual names; both `must_consider_residuals` are present.
- Quotation audit: 9 curly-quoted spans plus 5 `design_cite` values extracted mechanically and
  matched against `00` under whitespace/quote normalisation. **14 of 14 verbatim. No quotation in
  this node is fabricated or paraphrased inside quote marks.**
- No threshold, score, evidence count or handling class appears; the digits present are fixture
  filenames, identifiers and standard designations. No file example writes a folder path as a fact.
- `fields: []`, `template.dimension_order: []`, `also_holds_with: []`, `role_split: []` — each with
  a note stating the contract reason.
- Only the two assigned files were written. No neighbour node, roster, `canonical_fields`,
  `check.py`, `src/` or ownership register was touched.

## NEEDS-JOSEPH (this node only)

- **NJ-DWG-1 — is `drawing_number` a key at all?** (a) Keep it alongside `design_item`, accepting a
  same-entity/different-key `role_split` this row declined to write. (b) Fold it into `design_item`
  and lose the ability to say one item's three sheets are three documents. (c) Treat the identifier
  as pure grouping evidence and propose nothing, leaving the version family anchored on filename
  stems — cheapest, and weakest under rename. The row recommends (a) with
  `destination_eligible: false`; it does not decide.
- **NJ-DWG-2 — does this row own schematic and PCB sheet sets?** The honest problem: they carry an
  identical title-block cluster, identical sheet pagination and an identical revision-history
  table, so the row's entire structural signal is present and only the *content of the frame*
  differs. (a) Content-of-frame decides, as encoded today — one structural signal resolving three
  ways. (b) This row owns the title-block situation and schematic / PCB become
  `engineering_artifact_type` values inside it, which would make `engineering.electrical-schematic`
  and `engineering.pcb-layout` candidates for refusal. (c) Three rows share the situation and split
  on discipline, accepting a permanent three-way collision. This is the one open question that
  could still change whether this row or its siblings exist.
- **NJ-DWG-3 (reciprocates the schema's NJ-ENG-2) — revision as domain fact or version-family
  relation only?** This row recommends the latter and refuses the folder level *either way*. The
  warning attached: if R1c promotes `revision_or_baseline` to a domain fact, the refusal of the
  dimension must survive the promotion, because the promotion is exactly what would make the level
  look legitimate.
- **NJ-DWG-4 (reciprocates NJ-ENG-3) — plant and infrastructure sheet sets.** Do they activate both
  this row and `construction_property.drawings-revisions`, or does the reusable-item-versus-site
  seam decide exclusively? Encoded today as exclusive, with `Review Later` as the honest fallback.
- **NJ-DWG-5 — a RECOMMENDATION to R1c, not a question.** The absorbed legacy row
  `eng.gdt-tolerance` should be discharged as recognition signals inside this row plus the
  `manufacturing.inspection-record` and `engineering.standards-library` collisions. No tolerancing
  node should be created: its only evidence is a notation that is densest in two other rows' files,
  which makes it never-alone evidence, which means it could never activate.
- **NJ-DWG-6 — reciprocal edges owed.** No landed node names this id today. Eight collisions are
  authored from this side alone; `construction_property.drawings-revisions`,
  `manufacturing.inspection-record` and `engineering.cad-model` are the three where a one-sided
  edge would do real damage, because each shares fixture bytes with this row.
