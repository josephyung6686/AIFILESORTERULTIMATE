# engineering.process-plant-design — lab notes (R1b)

Depth: J-DEPTH
Date: 2026-08-26
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.process-plant-design.json`](engineering.process-plant-design.json).
No prior draft existed; both files are new and owned by this pass.

## The charge — the strongest case that this row should not exist

I put the case first because it nearly won, and because two landed siblings have already made it.

**The case for refusal.** "Chemical and process plant design" is an *industry vertical*, not a filing
situation. It names who employs the engineer, exactly as "aerospace" and "automotive" do two rows
below it on the roster. Every artefact it appears to own already has a sibling that owns it by shape:
a P&ID is a controlled drawing (`engineering.drawing-package`), a 3D plant model is a CAD model
(`engineering.cad-model`), an equipment list is a product structure (`engineering.bill-of-materials`),
a heat-and-material balance is a solver output (`engineering.simulation-analysis`), a HAZOP is a
hazard study (`engineering.risk-analysis-fmea`), a piping class is a material specification
(`engineering.material-specification`). On that reading the row is a *discipline container* whose
`work_types` are values of `engineering_artifact_type` and whose detection signals, dimensions and
privacy rules would all be the engineering schema's defaults — a textbook refusal under
CONNECTION.md's node test, and the 574's original mistake.

This is not a strawman I built to knock down. `engineering.commissioning-handover.research.md`
already rejected an edge to me in those words: this row and `engineering.civil-structural` are
"discipline containers whose evidence is design definition, already covered by the schema-level seam.
Adding edges would encode a discipline taxonomy this pass must not build."
`engineering.cad-model.research.md` refused an edge on the same ground, preferring the
`construction_property` seam because "a third claimant on the same evidence is worse than two."

**Why the case is nonetheless defeated.** The refusal is correct against the roster's *name* and
wrong against the *material*. What is actually on disk in this world is not a set of document types;
it is one relation that no other engineering row carries:

> a **tag** bound to a **numbered line or stream**, that line carrying a **service fluid** together
> with a **design pressure and design temperature** pair, with the tags related to one another by
> **connectivity** — a line runs *from* one tagged item *to* another.

That relation is not "an identified design item under revision control". It is topological where the
schema default is hierarchical, and it is a duty statement where the schema default is a control
statement. The decisive evidence is a negative one, and I would not have accepted the row without it:
**a line list and a stream table routinely carry no approval block, no revision block, no requirement
identifier and no drawing number at all.** The engineering schema default cannot fire on those files —
its three deterministic structures are title-block, requirements-trace and parent-assembly BOM, and a
line list has none of the three. Yet a line list is the single most load-bearing document in a
process design. A row whose best evidence is invisible to its schema's default is not a duplicate of
that default.

So the row survives, but not as issued. I have re-defined the `one_line` as the relation rather than
the industry, and raised **NJ-PLANT-4**: the shipped name and the shipped relation disagree.

Each of the seven forms of non-node was tested explicitly:

| Failure mode | Verdict |
|---|---|
| a `work_type` value | No. P&ID, line list and HMB *are* values (they are in `work_types`); the row is the relation that binds them, not any one of them. |
| a document type | No, for the same reason — twenty document types share one topology. |
| a lifecycle stage | No, and this cut the other way: FEED-versus-detailed-design **is** real here, and I deliberately demoted it out of the standing dimension order rather than let a stage masquerade as the node. |
| a medium, a length, a file format | No. `.dwg`, `.xlsx` and `.pdf` all carry the same relation; `never_alone` says extension alone never fires. |
| an organisation name | No, and this is the row's sharpest `never_alone`: operator, licensor, EPC contractor and vendor all appear in one title block and the name does not say which role it plays. |
| defined by an absence | Nearly — "engineering that isn't mechanical product design" would have been a refusal. Rescued by the positive tag/line/service/design-condition structure. |
| duplicate of a neighbour or of the schema default | Defeated above and argued file-by-file in the collisions section. |

## The node test, all three legs

**Leg 1 — detection signals differ.** Stated in full in the JSON's `node_test.leg_1_detection`. No
signal on either list implies a signal on the other, and the line-list case above shows the schema
default failing outright where this row succeeds.

**Leg 2 — recommended dimensions differ.** The schema's researched default is
`project → design_item → lifecycle_stage → engineering_artifact_type`. The second level cannot be
filled here. These files belong to a **process unit** — a bounded section of a continuous plant —
and a unit is not a parent item in a product structure: it has no assembly tree, its members are
tagged instances rather than child parts, and one tagged item legitimately appears on two units'
deliverables where a line crosses a battery limit. My researched order is
`project → plant/unit → engineering_artifact_type`, with `lifecycle_stage` demoted to an optional
branch because a plant corpus overwhelmingly sits in one stage and a standing gate level would open
branches the facts cannot fill. `dimension_order` in the JSON is `[]` under binding PR-6; the order
lives in `template.why` and is explicitly conditional on R1c.

**Leg 3 — privacy differs in kind.** The engineering schema's reason is proprietary IP and export
control — commercial confidence and national-security classification of *design content*. My reason
is different in kind: a HAZOP worksheet, a relief-scenario set and a cause-and-effect matrix state
where a hazardous inventory sits, how it is released, and which single safeguard stands between a
deviation and harm to **people who do not own the file**. That is third-party exposure, and it is why
this row is the only engineering sibling I found routing an inactive file to `Protected Records` by
default. That default is stronger than any sibling applies, so it is raised as **NJ-PLANT-3** rather
than assumed.

## Files considered and rejected

Naming what I kept would not be research. These are the tempting false positives:

- **Commissioning ITRs, punch lists, and the handover dossier for `P-2101A`.** Same tag, same plant,
  and the punch list even quotes the P&ID revision. Rejected: their relation is *completion of an
  activity on a located installed instance*, not what the plant is. `engineering.commissioning-handover`.
- **A weld log / NDE report for line `1502`.** I kept the *isometric* and rejected the weld record
  even though they share the line number: the isometric states what the line is, the weld log records
  execution against it. Manufacturing's side of the same seam as the asset register.
- **Operating procedures and shift-startup SOPs.** Written from the P&ID, tag-dense, and superficially
  the best match in the corpus. Rejected: they instruct a person to perform an operation.
  `manufacturing.work-instruction`.
- **A vendor pump performance curve from a catalogue.** Has flows, heads, materials — everything a
  datasheet has *except a tag*. Rejected: no tagged instance, no design duty for a specific service.
  Falls to `Reference Clips` or `engineering.material-specification`.
- **An emissions inventory / environmental permit return.** Genuinely derived from the design basis's
  utility and effluent summary. Rejected: its anchor is a regulator and a reporting period.
  `manufacturing.environmental-compliance` or `government.environmental-regulation`.
- **A piping-class specification treated as a *published standard*.** The class *specification the
  project issued* is mine; a bound copy of the industry code it cites is `engineering.standards-library`.
  This is the reason "a chemical or fluid name alone" and "a code designation" cannot activate.
- **A plant insurance schedule and a spare-parts holding list.** Both are lists of the same vessels
  and pumps, with tags. Rejected: neither carries a service or design condition; they are inventories
  of objects, not definitions of them. This is why "an equipment list alone" is on `never_alone`.
- **A `.hsc`-style native flowsheet simulator case file.** Rejected as a *file example* and kept only
  as a collision: its own relation is a run. See `engineering.simulation-analysis` below.

## The collision fixture

**`MEP-Chilled-Water-Schematic_Rev4_IFC.pdf`.** It is drawn with the same symbol set as a P&ID —
pumps, valves, a chiller, annotated pipework with sizes — it is under revision control, it has a
controlled title block, and a keyword detector would call it mine every time.

What discriminates it: **there is no line-numbering system, no service or design-condition columns,
and no datasheet reference.** Its anchor is a *building address* and a numbered contract drawing
series for one property, and its issue status is a contract issue. It is
`construction_property.construction-project` evidence, it keeps its construction facts, and it is
recorded in this row's `file_examples` with `also_schema: "construction_property"` so that the
correct outcome is written down rather than merely avoided.

A second, harder one is in the file list: **`Equipment-Register_Site-Assets_2026.xlsx`**, which
carries the *identical tags* to my flowsheets. Discriminated by column set — serial number,
installation date, criticality, maintenance strategy (as-installed) versus service fluid, design
pressure, design temperature and a from/to line relation (as-designed).

## Reciprocal boundaries, both directions, same fixture

- **`engineering.civil-structural`** — *already reciprocated from their side.* Their fixture: "a pipe
  rack or a plant support structure." Their statement: process apparatus is mine, the structure that
  carries it is theirs, and both may hold on one plant package. Mine, stated identically, and I
  additionally accept the offer in their **NJ-CIVIL-4**: if R1c prefers a single claimant, they
  concede the process apparatus and I concede the load-path justification. Symmetric, same fixture,
  same words.
- **`engineering.drawing-package`** — fixture `1042-PID-2100-001_..._RevD.pdf`. *Their direction:* the
  sheet is a member of a controlled set with a register and a transmittal. *My direction:* the sheet's
  content is a tag-and-line topology. A transmittal with no sheet content is only theirs; a line list
  with no drawing is only mine.
- **`engineering.simulation-analysis`** — fixture `HMB_Unit-2100_Case-2-Summer-Design.xlsx`. *Their
  direction:* a solver run with convergence and case configuration. *My direction:* the balance as
  issued design basis bound to published stream numbers. A native case file is only theirs; a stream
  table with no run information is only mine; a report exported straight from a case sits in both.
- **`engineering.bill-of-materials`** — fixture `Line-List_Unit-2100_RevC.xlsx` and the isometric's
  take-off. *Their direction:* parent assembly to child part with quantities. *My direction:*
  from-tag to to-tag, which is connectivity, not containment. I concede any plant table that *does*
  state a parent/child product structure.
- **`manufacturing.asset-register`** — fixture `Equipment-Register_Site-Assets_2026.xlsx`. *Their
  direction:* the as-installed asset. *My direction:* the as-designed duty. The shared tag belongs to
  neither, which is why it sits on `never_alone`.
- **`engineering.commissioning-handover`** — fixture: a marked-up P&ID stamped as-built. *Their
  direction:* completion of transfer of an installed instance. *My direction:* the definition,
  including the as-built revision folded back into it. **Asymmetry recorded:** they declined this
  edge. Their refusal was reasonable against the roster's industry framing and is answered by the
  relation argued here; I have written the edge from my side only and flagged it in **NJ-PLANT-5**
  rather than silently agreeing or silently disagreeing.
- **`engineering.cad-model`** — fixture: a 3D plant model of Unit 2100. Same asymmetry, same
  treatment, with an explicit instruction in the edge text: if R1c agrees with cad-model, delete the
  edge *from my file*, not from theirs.
- **`engineering.risk-analysis-fmea`** — fixture `HAZOP-Worksheet_Node-7_...xlsx` against a design
  FMEA. *Theirs:* the row key is a component's failure mode scored by severity, occurrence, detection.
  *Mine:* the row key is a guideword deviation on a node bounded by lines. A component-scored study in
  a plant is theirs; a node-walked study on a machine is mine.
- **`code.software-project`** — fixture: a control narrative against an exported PLC/DCS
  configuration. *Theirs:* repository root, manifest, source structure. *Mine:* intended plant
  behaviour stated by tag, interlocks specified in a cause-and-effect matrix. A control-system
  integrator's repository is code even though its employer designs plants.
- **`research.dataset-analysis`** — fixture: a pilot-plant campaign dataset. *Theirs:* a generalisable
  proposition about the chemistry. *Mine:* a scale-up basis feeding one named unit's design basis. The
  tell is whether the conclusion is about a substance or about a plant.

## `proposed_fields` — empty, and why that is the researched answer

Three keys were tempting; all three were rejected, and the reasoning is in
`proposed_fields_note`. In short:

1. **A plant/unit key.** The row genuinely needs this level — leg 2 depends on it. Proposing it now
   mints a near-synonym of the schema's own unadjudicated `design_item`, which is precisely what
   `engineering.civil-structural` declined to do for `structure`. Recommendation to R1c is (a) widen
   `design_item`. **NJ-PLANT-1**.
2. **An equipment/instrument tag key.** The best fact on the node. It cannot be a destination — a
   folder per pump, valve and transmitter is indefensible — so it could only exist as a search and
   grouping fact, and whether the shared vocabulary permits such a fact is not a template's decision.
   **NJ-PLANT-2**.
3. **A service / design-condition key.** Multi-valued per file and per row, so it fails destination
   eligibility for exactly the reason `engineering.civil-structural` gave for `design_code`.
   Duplicating an unresolved question is worse than recording it.

`fields: []` by contract (a template references its schema's fields and never copies them) and by
PR-6. `proposed_context_terms` are marked PROPOSED for R6, not design — `00` states the
pattern-plus-context shape for course codes only and does not list these.

## Sparse-file and grouping discipline

`stream_table_crop.png` is this node's `HW 3.pdf`: a cropped screenshot of a numeric table, no legible
tag or stream number, no EXIF, sitting beside accepted Unit 2100 files. It is marked
`group_without_copying_facts: true`, its `facts_legal` is universals only, and its
`must_not_conclude` covers both halves — no unit copied from neighbours, and missing EXIF is not
proof of a screenshot. The first `grouping_reasons` entry is the interesting one: a tag threads a
pump's P&ID sheet, datasheet, relief case and isometric into one neighbourhood *even though no two of
those files share a title-block field*. Activation is not grouping.

## Neighbours considered that got no edge

- **`engineering.project` / `business_operations`** — a plant project's schedule, cost report and
  progress S-curve are dense with unit names. No shared *discriminating* evidence: the schema row's
  `Sprint-14-Project-Status.xlsx` fixture already carries this seam and a third claimant adds nothing.
- **`engineering.requirements-specification`** — a process design basis is requirement-flavoured, but
  its slots are capacity, feed spec and utilities, not stable requirement identifiers with
  verification methods. Different structure, no confusion.
- **`engineering.material-specification`** — real overlap on piping class specifications. Left as a
  concession in prose rather than an edge: a class spec that names no unit and no service is theirs.
- **`manufacturing.safety-case`** — close on hazard language, but a safety case argues that an
  *operating* installation is acceptable to a regulator. Covered by the `manufacturing`
  co-activation.
- **`government.permit-licensing` / `government.environmental-regulation`** — the permit application
  quotes the design basis, but its anchor is a regulator and an application reference.
- **`role_split`** — empty, and this is the interesting refusal. The split this material most wants is
  **process licensor / engineering contractor / owner-operator**, all three of which appear in one
  title block and any of which the name might denote. No canonical key exists for any role,
  authorship is never a destination under `00`, and minting a producer-side key for one template is
  the move that generated thousands of private field names. Recorded in the `never_alone` rule on
  operator and contractor names instead.

## Audits run before returning

- `python3 -m json.tool` — parses.
- Four `00` spans are quoted, all in `falls_through_to.design_cite` (Independent Records, Review
  Later, Unsupported or Encrypted, Protected Records). All four were grepped out of
  `planning/00-database-agent-product-design.md` verbatim before being written. No other quotation
  marks in either file attribute text to `00`.
- All 13 `file_examples.source_type` values are in `SOURCE_TYPES`.
- All 11 `collides_with.domain` values are roster ids (verified against `planning/domains/roster.json`).
  Both `also_holds_with.domain` values are schema ids **and** are on the engineering schema row's own
  declared co-activation set — the code and research relations are expressed as collisions precisely
  because a template may not widen its schema's edges.
- All four `falls_through_to.residual_template` names are `00` residual names.
- `dimension_order` is `[]` per PR-6; `fields` and `proposed_fields` are `[]`.
- No threshold, score, count or handling class appears; `sensitivity` is `potentially_sensitive`.
- Only the two assigned files were written. The ownership register, the roster, canonical fields and
  every neighbour node were read but not modified.

## NEEDS-JOSEPH (this node only)

- **NJ-PLANT-1 — the intelligible parent is a process unit, and `design_item` is item-shaped.**
  (a) widen `design_item` to cover a bounded section of a continuous plant — recommended, and the
  reason no key was proposed; (b) mint a plant/unit key, creating two near-synonyms before either is
  adjudicated; (c) collapse units into `project`, losing the level that makes a line number and a
  deviation node intelligible.
- **NJ-PLANT-2 — may a non-destination domain fact exist at all?** The tag is this row's strongest
  fact and its whole grouping story, and it can never be a folder level. If the shared vocabulary
  admits only destination-eligible facts, `grouping_reasons` must be re-expressed without it.
- **NJ-PLANT-3 — does an inactive hazard study default to `Protected Records`?** This row says yes,
  on third-party-exposure grounds. That is a stronger default than any engineering sibling applies.
  Confirm, or route it to `Review Later` with the rest of the ambiguous technical material.
- **NJ-PLANT-4 — the roster name is an industry label; the researched relation is a topology.** If
  roster names are frozen, the shipped file's name and its `one_line` disagree. Renaming to something
  like "process plant design definition (tag, line and stream)" is recommended.
- **NJ-PLANT-5 — two landed siblings declined edges to this row as a "discipline container".**
  `engineering.cad-model` and `engineering.commissioning-handover` both refused, reasonably, against
  the industry framing. Edges are written from this side only, each flagged in its own text. R1c
  should reconcile the asymmetry in one direction rather than let one side stand silently.
