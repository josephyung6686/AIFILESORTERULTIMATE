# engineering.cad-model — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.cad-model.json`](engineering.cad-model.json).
Verdict: **node survives**, on two of the node test's three legs, with the third declined explicitly.
No sibling engineering template was landed when this row was written, so every edge below is this
side's proposal for R1c to reciprocate.

## Sources actually used

- `RESEARCH-BRIEF.md` and the stamped assignment (`make_prompt.py engineering.cad-model`).
- `planning/00-database-agent-product-design.md` — read by targeted grep only. Every span in quote
  marks below was matched verbatim against it by script under whitespace/curly-quote normalization.
  Load-bearing passages: the design/CAD/3D extractor requirement, extension-as-routing, the archive
  no-extraction rule, the download-session rule, and the residual library.
- `planning/domains/nodes/engineering.json` — **the schema anchor I am measured against.** Its
  `work_types`, `recognition.deterministic`, `template.why`, `proposed_fields.revision_or_baseline`
  and `also_holds_with` set each constrained this row directly. `engineering.research.md` was not
  opened: the JSON left nothing about the node test undecided.
- `planning/domains/nodes/finance.crypto-assets.research.md` — depth calibration, one launch row.
- `planning/domains/roster.json` — every edge endpoint resolved mechanically, and where the row
  changed shape: the assignment named three neighbours (`manufacturing`, `code`, `research`), but the
  real competition is a dozen sibling engineering templates it never mentioned — above all
  `engineering.drawing-package` and `engineering.standards-library` — plus `creative.3d-asset`.
- `grep -rl "engineering.cad-model" planning/domains/nodes/` — **no landed row argues a boundary
  against this one.** Nothing to align to; nothing rewritten.

## THE CHARGE: the strongest case that this row should not exist

I put four independent kill arguments before writing anything, because three of them are the
project's own recorded failure modes and one of them is written into my schema anchor by name.

**1. It is a work_type value, and my own schema says so.** `engineering.json`'s `work_types[]`
contains the literal entry `CAD model`, under a note reading: *candidate VALUES of
`engineering_artifact_type` ... not child schemas.* The schema anchor pre-emptively refuses this
row. If "CAD model" is a value of the artifact-type field, then a template whose whole content is
"the files that carry that value" is a folder query, not a node. This is the strongest of the four
and it is the one that had to be defeated by mechanism, not by protest.

**2. It is a file-format row.** `.sldprt`, `.step`, `.stl`, `.f3d`. Extensions are routing signals
and `SOURCE_TYPES`, never nodes — 00 is explicit that the engine should *"treat the file extension
as a routing signal rather than an assumption about meaning"*. Any row that would fire on a set of
extensions has failed before it starts.

**3. It is a lifecycle stage.** The roster's own hint frames the row as *before and beside the
drawing that releases it*. "Before release" is a position on `lifecycle_stage`, a field the schema
already proposes. Defining a node by where material sits on one of its schema's own fields is
duplication with extra steps.

**4. It is a row defined by an absence.** The tempting definition is "engineering geometry that is
not yet a released drawing." A row whose distinguishing property is the absence of something cannot
activate, because absence is not evidence.

### How the charge is defeated

Arguments 2, 3 and 4 fail against the same finding, and argument 1 fails against a different one.

**Against 2, 3 and 4: the row's actual discriminator is a relation between files, and it is
positive.** An assembly container's extracted *linked asset names* resolve to sibling component
files present on disk. That is a resolved reference edge — positively observable, format-neutral,
and it fires on a `.SLDASM`, a `.CATProduct` or an `.iam` alike while refusing a `.stl` in the same
directory. 00 licenses this mechanism directly and by name for exactly these formats: *"Design and
creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum
yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards
where accessible, linked asset names, and preview text."* `linked asset names` is the phrase this
row is built on. The definition is therefore not an extension, not a stage, and not an absence.

**Against 1: the value's own detection mechanism is unlike every other value's.** Every
deterministic signal on the engineering schema row is a *labelled-slot relation inside one
document* — title block, requirement rows beside verification columns, TDP manifest, change block
with affected item, BOM parent/child, analysis inputs/results, verification matrix. A native
geometry container has no page, no sheet, no rows, no approval slot; running the schema's default
detector across a CAD tree finds nothing. If a value's material is invisible to its own schema's
detector, a template that supplies the missing detector is doing work the field cannot do.

**What would have made me refuse.** If the only distinguishing content had been "these files are
CAD," or if the row had needed a new field key to exist, I would have refused and routed to
`Review Later` and `Independent Records`. It needed neither: `proposed_fields` is empty.

## The node test, all three legs

**Leg 1 — detection signals differ from the schema default. YES.** Three positive discriminators,
none of which appears on `engineering.json`: (a) the resolved reference edge above; (b) a
container-metadata property block carrying labelled part-number, description, material and revision
slots *inside a file that has no sheet and no approval slot* — read by the design/creative
extractor, not the text extractor; (c) a same-stem format swarm, where one geometry stem appears as
native container, neutral exchange file and mesh export, so duplicate-family and version-family
signals cross format boundaries instead of tracking one extension. (b) carries a second job: the
*absence* of the sheet/approval pair is half the discrimination against `engineering.drawing-package`
— used as a tiebreak between two positively-evidenced candidates, never as the activation itself.

**Leg 2 — recommended dimensions differ. YES, and they are shorter.** The schema's researched
default is `project → design_item → lifecycle_stage → engineering_artifact_type`. Two of those four
collapse here. `engineering_artifact_type` resolves to one value across the entire corpus, and a
level with one child is not a level. `lifecycle_stage` is rarely carried in a labelled maturity slot
inside a geometry container, so opening it forces the value to come from a filename suffix or a
filesystem date — which the schema row itself refuses, saying that filename `revC`, `final`, `_v7`
and filesystem dates remain possible observations that activate nothing alone. What remains is
`project → design_item`, with `design_item` taken at the **assembly** level and parts sitting under
their parent assembly, for 00's parent-makes-child-intelligible reason: a component identifier is as
meaningless without its assembly as Homework 3 is without its course. Both the length and the
derivation differ — this is the only engineering situation where a dimension's value comes from a
link graph rather than from a slot.

`dimension_order` in the JSON is nevertheless **empty**, because PR-6 leaves the engineering schema
with no destination-eligible fields declared and a machine-readable order must not be encoded before
its keys are legal. The researched order lives in `template.why`, exactly as the schema anchor does
it.

**Leg 3 — privacy rules differ. NO. Declined.** Geometry is the most directly exfiltratable form of
a design definition — a neutral export is by itself enough to have a part made elsewhere — and
export-control and supplier-confidentiality exposure attach to the same bytes. But the schema is
already `potentially_sensitive`, and this is a difference of degree, not of kind. I am not claiming
this leg. Two of three is what CONNECTION requires, and inflating the third would be padding.

**One extra property, stated as a filing rule and not smuggled into leg 3.** Native assemblies
resolve their components by stored path and filename, so a per-file move a user accepts can leave
the assembly unable to open. This is the only engineering row where accepting a reorganization
proposal can destroy the file's own readability. It is marked `inference` (an observed property of
mainstream parametric CAD systems, not a claim from 00) and it is raised as NJ-CAD-1 rather than
decided.

## Files considered and rejected

Naming what this row does **not** hold was the larger half of the work, because almost everything
adjacent is also geometry.

- **`BPA-210-001_RevC.pdf` / `.dwg` sheet** — shares my stem, directory and item. Rejected: its
  evidence is a title block, a revision table and an approval slot. `engineering.drawing-package`.
- **`BPA-210_Product-Structure.xlsx`** — derived from my assembly and names my parts. Rejected: a
  table of rows is the schema's default detector, not mine. `engineering.bill-of-materials`.
- **A meshed FEA input deck / `.cgns`** — geometry, same stem. Rejected: a defeatured idealisation
  carrying element definitions and load cards. `engineering.simulation-analysis`.
- **`BPA-210-001_OP20.nc` toolpath, `.gcode`** — generated from my geometry. Rejected: an execution
  instruction is manufacturing regardless of which model produced it.
- **`Core_Cavity.SLDASM`** — structurally *identical* to my strongest fixture: assembly, resolved
  components, part numbers. Rejected because the item it defines is the tool, not the product. This
  one is uncomfortable and is why R1c should check my `manufacturing.tooling-fixture` edge.
- **`bracket_render_final.png` / a KeyShot scene** — output of my geometry. An image.
- **`~$assembly.SLDASM`, `bracket.SLDPRT.bak`, lock and swap files** — machine detritus; evidence
  *of* a version family, not records to file.
- **`schematic.kicad_sch` / `board.kicad_pcb`** — tempting because both are called "the model" in
  speech. Rejected: copper, nets, stackup. `engineering.electrical-schematic`, `engineering.pcb-layout`.
- **`Level-02_Structure.ifc`** — kept as a file example rather than merely rejected, because
  `construction_property` (site/building/storey hierarchy) is the answer a 3D-model-shaped detector
  gets wrong.

## The collision fixtures

Two, because they fail in opposite directions and a detector that catches one can still be fooled by
the other.

**`3DBenchy.stl`, downloaded.** Tessellated mesh geometry, in a folder called `3D Prints`,
`design_creative`-adjacent, arriving with a licence text file and a slicer profile. It satisfies
every naive signal this row could have used: 3D, geometry, CAD-ish folder, engineering-looking. It
is not this row. Discriminators, all positive: no feature history, no authored property block, no
linked assets, no native sibling, and no downstream artifact naming it. Its arrival is a bounded
download session, and 00 states that *"A session should never be treated as proof of topic."* Routes
to `Review Later`. Note it is also **not** `engineering.prototype-build` — that row needs a build
record naming a design item, and a licence file is not one.

**`91251A537.STEP`, a supplier catalogue fastener.** This is the harder one, and it is the fixture I
would put in a regression suite. It is a real exchange file, with a part-number-shaped stem, sitting
in a genuine CAD directory, and **an accepted assembly of mine resolves it as a component** — so it
passes my primary discriminator, the reference edge. It is still not mine. What discriminates it:
the identifier belongs to a vendor catalogue rather than to this user's design, its header
description carries a size and grade instead of a design description, no local property block was
authored, and it sits among dozens of similarly numbered siblings with no native counterparts. It is
reference material the design *uses*, not the definition the design *produces*.
`engineering.standards-library`; residual `Independent Records`. It is marked
`group_without_copying_facts: true` — it may sit in the assembly neighbourhood and must not receive
the assembly's `design_item`.

## Reciprocal boundaries, same fixture named on both sides

- **`engineering.drawing-package`** — mine: the geometry container the sheet is generated *from*;
  theirs: the sheet that *releases* it. Shared bytes: `BPA-210-001_Bracket.SLDPRT` and
  `BPA-210-001_RevC.pdf`, same stem, same directory. I must not take the PDF because the stem
  matches; they must not take the SLDPRT because it carries a revision *property*, since a property
  slot is not a revision table with an approval. The `.dwg` container holds both kinds and is
  separated only by the presence of sheet structure.
- **`creative.3d-asset`** — mine: geometry whose destiny is a physical part (millimetre units,
  material and part-number properties, a parent assembly, a sheet or BOM naming it); theirs:
  geometry whose destiny is an image or a runtime (materials, UVs, rigs, lights, render output).
  Shared bytes: `enclosure.obj` — theirs beside textures and a scene file, mine beside a native
  parametric sibling with an item identifier. `hero_prop_highpoly.blend` is theirs even inside an
  engineering directory.
- **`engineering.standards-library`** — as above; `91251A537.STEP` named on both sides.
- **`engineering.simulation-analysis`** — `BPA-210-001_RevC.STEP` is mine as the design definition,
  theirs only as a named input recorded inside a study; a file carrying element definitions and load
  cards is theirs even when its stem matches mine.
- **`engineering.industrial-design`** — `Housing_ClassA.3dm` is theirs beside renders and colour
  studies, mine when an assembly's linked asset names resolve to it. **Not settled** — NJ-CAD-3.
- **`manufacturing.tooling-fixture`** — `BPA-210-001_OP20.nc` and `Core_Cavity.SLDASM` are both
  theirs, the second despite being structurally identical to mine.
- **`engineering.pcb-layout`** — `board.step` is mine when an enclosure assembly resolves it as a
  component, theirs inside a fabrication package beside layer and drill outputs.
- **`engineering.prototype-build`** — `bracket.stl` is mine when a native parametric sibling and an
  item identifier exist, theirs inside a build record naming machine and material.
- **`construction_property`** — `Level-02_Structure.ifc` stays theirs; a modular plant skid
  manufactured repeatedly is mine even when installed at one site.

## `proposed_fields`: empty, deliberately

Rule 12 keeps `fields` empty; the legal set is whatever R1c licenses from the engineering schema
row. `proposed_fields` is empty by argument, not by omission. The one key this material makes
tempting is a **parent-assembly identifier**, and minting it would be `design_item` under a second
spelling to solve one template's problem — the exact move that produced thousands of private field
names in the overnight pass. The hierarchy question goes to NJ-CAD-2 instead. A **part identifier**
is likewise not proposed: a short alphanumeric token is a stock code, a purchase line, an asset tag
or a vendor catalogue number, and `91251A537.STEP` is the fixture that proves it. It is evidence,
never a key.

`role_split` is empty and the refusal is informative: the split this material wants is the assembly
that *owns* a component against the assembly that merely *references* a purchased one — both roles
would need `design_item` with opposite meanings, and there is no canonical producer/consumer key to
split against. Recorded in that fixture's `must_not_conclude` instead.

## Sparse-file discipline

Three fixtures carry `group_without_copying_facts: true`. `bracket_v7_FINAL_fixed.SLDPRT` is this
row's `HW 3.pdf`: an empty property block, nothing referencing it, three near-identical siblings, and
an accepted assembly next door — it may join that neighbourhood and must receive nothing from it,
least of all a revision read off `FINAL`. The viewport screenshot and the catalogue fastener are the
other two.

## Neighbours considered that did **not** get an edge

- **`code.software-project` as a collision** — declined. The relation is co-activation, already
  carried by `also_holds_with: code` on `bracket.py`; asserting both about one file is contradictory.
- **`research.dataset-analysis`** — a geometry file is not a dataset; the study-input relation is
  covered by `engineering.simulation-analysis` and by `also_holds_with: research`.
- **`photos.scanned-documents`** — a photographed drawing is a scan of a *sheet*; that competition
  is drawing-package's, not mine.
- **`engineering.civil-structural` / `engineering.process-plant-design`** — real overlap on plant and
  structural 3D, but `construction_property` already carries the site-versus-product seam with a
  named fixture, and a third claimant on the same evidence is worse than two.
- **`creative` as `also_holds_with`** — refused on contract grounds: it is not in the engineering
  schema row's declared co-activation set, and a template must not widen its schema's edges. The
  relation is expressed as a collision against `creative.3d-asset`.
- **`engineering.invention-disclosure`** — geometry appears there as a figure; that row's evidence
  is legal, not geometric.

## Audits run before returning

- `python3 -m json.tool` — parses; 34 keys, aligned to `engineering.json`'s idiom.
- All five `00` spans in quote marks matched **verbatim** under whitespace/curly-quote
  normalization, by script, against `planning/00-database-agent-product-design.md`. No fabricated
  quotation.
- 11/11 `file_examples.source_type` values are in `SOURCE_TYPES`.
- 9/9 `collides_with` targets resolve to roster ids (8 node ids, 1 schema id); 2/2
  `also_holds_with` are roster schema ids **and** members of the engineering schema row's declared
  set; 4/4 `falls_through_to` names are §7.3 residuals.
- `fields: []`, `proposed_fields: []`, `dimension_order: []` — PR-6 respected.
- No threshold, score, count or handling class anywhere; `sensitivity` is `potentially_sensitive`
  only. No file example writes a folder path as a fact.
- Only the two assigned files were written. No neighbour node, roster, canonical_fields, check.py,
  src/ or SPEC was touched.

## NEEDS-JOSEPH (this node only)

- **NJ-CAD-1 — relocation is destructive here and nowhere else in engineering.** Native assemblies
  resolve components by stored path and filename; a per-file move the user accepts can leave the
  assembly unable to open. Three answers: (a) cad-model files are index-and-link only and never
  proposed for a move — safe, but strands a large corpus; (b) proposals are made only at the whole
  resolved-reference-set granularity, moving the reference closure together — **recommended**;
  (c) per-file proposals with a warning, which puts the consequence on the user. This is product
  policy about what the mover may do, not a template's decision. **Recorded, not resolved.**
- **NJ-CAD-2 — CAD is hierarchical and the schema offers one `design_item` key.** (a) `design_item`
  takes the top assembly for all members, part identity searchable but never a dimension —
  **recommended**; (b) per-file, which yields one folder per part and destroys the assembly
  grouping; (c) mint a parent-assembly key — refused here as a duplicate spelling of `design_item`.
- **NJ-CAD-3 — the industrial-design seam is genuinely unsettled.** Is a Class-A surface master this
  row's controlled geometry, `engineering.industrial-design`'s form work, or both when both
  neighbourhoods are present? The row states a preference (downstream reference decides) and does
  not pretend it is settled.
- **NJ-CAD-4 — which residual owns a readable-but-uncontextualised native container.**
  `Review Later` fits because its meaning is partly understood; `Unsupported or Encrypted` fits
  because 00 requires unsupported proprietary formats to be *"recorded as indexed-but-unreadable
  rather than silently treated as empty"* and geometry is opaque even when metadata is not. The row
  prefers `Review Later` when metadata is readable and `Unsupported or Encrypted` when the container
  cannot be opened at all. Confirm, or invert.

## Recommendations for R1c (cross-row; not made here)

1. `engineering.drawing-package` should reciprocate on the same stem pair
   (`BPA-210-001_Bracket.SLDPRT` / `BPA-210-001_RevC.pdf`) and state that a revision *property* in a
   geometry container does not make it the released definition.
2. `engineering.standards-library` should carry `91251A537.STEP` as its own fixture — it is the
   sharpest false positive here and the sharpest true positive there.
3. Check the `manufacturing.tooling-fixture` edge. If R1c decides tool geometry activates
   `engineering.cad-model` with a manufacturing co-activation instead, this row's collision must be
   rewritten, not patched.
4. NJ-ENG-1/NJ-ENG-2 from the schema row bear on this template, but not fatally: if canonical
   `stage` and `artifact_type` are widened rather than made role-specific, the argument for dropping
   both levels survives unchanged, because it is about evidence, not key names.
