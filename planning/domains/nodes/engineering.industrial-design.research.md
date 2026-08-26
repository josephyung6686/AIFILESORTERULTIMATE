# engineering.industrial-design — lab notes (R1b)

Depth: J-DEPTH
Date: 2026-08-26
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.industrial-design.json`](engineering.industrial-design.json).
Salvage: none — no prior JSON, no prior memo, and no sibling `engineering.*` template had landed.
Verdict: **node accepted** on all three legs, after a serious attempt to kill it.

## Sources actually used

- The stamped assignment (`make_prompt.py engineering.industrial-design`): neighbours manufacturing,
  code, research; residuals Independent Records, Review Later; `inherited_field_keys: []`.
- `planning/domains/nodes/engineering.json` — the schema anchor, read in full. It did most of the
  work below: its ten deterministic signals, its default dimension order, its `also_holds_with` set
  and its `sensitivity_why` are what this row had to differ from.
- `planning/00-database-agent-product-design.md` — grepped, not streamed. One line (the residual
  library paragraph) supplied all five `design_cite` strings, matched character-for-character.
- `planning/domains/canonical_fields.json` — all 37 keys enumerated mechanically. None names an
  appearance variant; that is what licenses the single proposal.
- `planning/domains/roster.json` — every edge endpoint checked against the node list.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the depth calibration. Two things
  came from it beyond depth: a template must not widen its schema's `also_holds_with`, and the
  activation/grouping firewall belongs in a named fixture rather than an assertion.
- `src/evidence_shape/vocabulary.py` — every `source_type` checked against the fourteen.

**Bottom-up reality checks** (no gazetteer content, no regex, no threshold created): CMF is a real
standing role whose deliverable is a matrix of colourways against colour standard / substrate /
process / gloss. Appearance cannot be specified to a number the way a dimension can, so it is
controlled by an approved physical exemplar plus a stated range — the real terms are *master
sample*, *limit sample*, *boundary sample*. Mould-texturing houses publish catalogue codes (the
`MT-#####` shape is the well-known Mold-Tech convention) and a texture is specified per part face
with a minimum draft angle, because deeper texture needs more draft to release. PPAP carries a
separate *Appearance Approval Report* element for parts with colour, grain or texture requirements —
a supplier *conformance* document, and the sharpest collision on this row. Design-intent exterior
surfaces are judged by continuity between patches and by highlight/zebra analysis, not tolerance.

## THE CHARGE — the strongest case that this row should not exist

I wrote the prosecution before the defence, and it is genuinely strong.

1. **"Industrial design" is a discipline name — never-alone evidence.** Same class of token as an
   organisation name or a job title. The engineering schema already forbids "a company, laboratory,
   client or standards-body name alone", and an ID team or consultancy is exactly that. A row named
   for a profession is this project's signature failure.
2. **Every artifact it names is a `work_type` value.** Concept sketch, render, CMF specification,
   appearance model record — these drop straight into the schema's proposed
   `engineering_artifact_type` enum beside "CAD model" and "engineering drawing". Extending an enum
   costs nothing and needs no node.
3. **It may be a medium.** "Sketches and renders" describes file media — images and 3D — and medium
   and file format are disqualifying bases for a row.
4. **It may be a lifecycle stage.** ID clusters at the front of development. If the row is really
   "the early part of engineering", it is a value of the schema's own proposed `lifecycle_stage`.
5. **Leg 2 looks structurally unavailable.** PR-6 leaves the engineering schema `fields: []` and so
   every engineering template must write `dimension_order: []`. If two rows both write `[]`, in what
   sense do their dimensions differ?
6. **Privacy looks identical.** Engineering is already `potentially_sensitive` for proprietary
   design definition. A render of an unreleased product is proprietary design definition.

Four of those are correct as far as they go. Here is why the row survives anyway.

## The node test, argued

### Leg 1 — detection signals differ from the default template. **PASS, decisively.**

I ran this row's file list against the engineering schema's ten deterministic signals: controlled
title block with drawing number and revision; requirements structure with stable identifiers and
verification-method columns; technical data package manifest; engineering-change structure with
current/replacement revisions; design-authoritative BOM with parent/child and quantities; analysis
comparing margins to named requirements; verification matrix linking requirement identifiers to
pass/fail; prototype configuration reconciliation; an archive manifest exposing several of those;
parent-folder context as a plausibility raiser only.

`BPA-210_CMF-Specification_Colourway-Matrix_v3.xlsx` fires **none** of them — no drawing number, no
requirement identifier, no verification method, no parent/child quantities, no margin, no pass/fail.
`Appearance-Approval_..._Master-Sample-MS-014.pdf` fires none either: it is an approval, but of a
*physical exemplar as a standard*, not of a change to a controlled revision.
`Concept-Sketches_Round-2_Directions-A-C.pdf` fires none.

The counterfactual is therefore concrete rather than rhetorical: **delete this row and the
appearance half of product development is not filed under a generic default — it is not recognised
at all**, and each file lands in Reference Clips, One-Off Images or Review Later. That is not a
template duplicating its default; it is a template supplying signals the default lacks.

The distinguishing structure, stated once: *a binding, for one identified part, between a named
appearance variant and a colour standard, a material, a finish or texture process, and a gloss level
— or the approved physical exemplar that stands in for all of it.* Nothing in the engineering
default looks for that, because dimensional and functional definition never needs it.

This answers prosecution point 2. The artifacts *are* enum values — I list them as values and say so
in `work_types_note`. But "rows are colourways; columns bind a colour standard, a substrate, a
process and a gloss level" is a recognition rule, not a value, and the schema does not contain it.
A node is justified by its signals, not by its nouns.

### Leg 2 — recommended dimensions differ. **PASS, form of point 5 conceded.**

Point 5 is right that both machine orders are `[]`, and I have not smuggled an order in. But
"differ" is a claim about the researched recommendation, which engineering.json itself states in
prose for exactly this reason. Like for like:

- schema default: `project → design_item → lifecycle_stage → engineering_artifact_type`
- this row: `project → design_item → colourway → engineering_artifact_type`

The third level changes, and the reason is structural. **A colourway is not a revision.** Rev B
supersedes Rev A; Graphite does not supersede Sand. They coexist, ship together, and each has its
own master sample, approval and render. Every sequential mechanism the schema offers —
`version_family`, its proposed `revision_or_baseline`, its revision-block signals — models
supersession, and modelling concurrent shipping siblings with a supersession relation is simply
wrong. That mismatch forces both the proposed key and the changed level, and it is why NJ-IDS-4
asks whether a concurrent-sibling relation should exist at all.

Second, `lifecycle_stage` is a poor level *here* even where it is good elsewhere: appearance corpora
carry a labelled variant slot far more often than a labelled gate, so the default's third level
opens branches the facts cannot fill. The collapse rule is written into the template `why` — with
one colourway, drop the level rather than produce a single-child branch.

### Leg 3 — privacy rules differ in kind. **PASS; point 6 answered.**

Both rows are `potentially_sensitive`; a two-value vocabulary cannot express the difference. The
difference is in the rule, twice over.

*Exposure surface.* Engineering's stated concern is proprietary definition, export control and
safety analysis — textual, and largely useless without context. Appearance is the opposite: one
render or one appearance-model photograph discloses the entire unreleased product to anyone who
glances at it. The protected surface here is **images and thumbnails**, not text. Different rule,
not a stronger one.

*Rights, not confidentiality.* Appearance corpora routinely contain material the user does not own:
purchased HDRIs and texture libraries, licensed typefaces embedded in a packaging render, mood-board
photographs that are somebody else's copyrighted work. Rights encumbrance points the *other* way
from secrecy — the risk is redistribution, not leakage — and engineering's `sensitivity_why` does
not mention it. `Moodboard_Nordic-Minimal.pdf` carries `must_not_conclude: "that collected imagery
is the user's own work"` for this reason. No handling class is assigned.

### Disposing of points 1, 3 and 4

**1 (discipline name).** Conceded and encoded rather than argued away: `never_alone` states that
"industrial design", "ID" and "CMF" as words, and any studio, agency, consultancy or colour-house
name, activate nothing; signal 10 lets a discipline-named folder raise plausibility only *after* a
real structure is present. The row could be renamed `engineering.appearance-cmf` without changing a
single signal — which is itself proof the discipline word does no work.

**3 (medium).** The evidence is not images. Four of the strongest fixtures — CMF matrix
(spreadsheet), approval (text_document), texture sheet (text_document), handoff (archive) — are not
images, and the two image fixtures are the *weakest*: the render is discriminated by embedded
renderer metadata, and the review photograph is a `group_without_copying_facts: true` case that
activates nothing.

**4 (lifecycle stage).** The hardest to dismiss, and it is dismissed by the back end of the row.
If ID were merely "early", CMF specifications, master samples, appearance approvals and texture
application sheets would not exist — those are late, production-facing, issued while the product is
being tooled. The row spans concept to production release, which a lifecycle stage cannot do.

## Files considered and rejected

- **`Moodboard_Nordic-Minimal.pdf`** — the collision fixture; see below. → **Reference Clips**.
- **`Packaging_Dieline_Pantone-2985C.ai`** — second-most tempting, because the colour-standard token
  is *identical* to one that legitimately appears in this product's CMF matrix. Rejected: the token
  binds ink to a printed substrate, accompanied by dielines, bleed and a print run, not by a resin
  and a gloss level. → `creative.graphic-design-project`. Kept as a file example so the row states
  its own false positive.
- **`PPAP_Appearance-Approval_Supplier-Vertex_PSW-2201.pdf`** — the authority runs the wrong way: it
  demonstrates conformance to a standard rather than establishing one. → `manufacturing.supplier-qualification`.
- **`BPA-210_Class-A-Surfaces_RevB.stp`** — kept but demoted: `also_schema: null`, activation from
  the extension forbidden. The container is `engineering.cad-model`; only the appearance intent
  stated *about* it is this row's.
- **A resin datasheet giving tensile modulus and flammability for the same shell** — not written as
  an example because it is unambiguously `engineering.material-specification` even though it names a
  colour. Material as performance ≠ material as appearance.
- **A marketing launch hero image, same product, same colourway** — pixel-identical to the render
  fixture and rejected: once announced, the same image is a campaign asset with a campaign, channel
  and usage window. The discriminator is the campaign structure, not the image; listed under
  `needs_llm` rather than given a deterministic rule.
- **A tooling drawing for the mould that produces the textured shell** — `manufacturing.tooling-fixture`.
  The texture *specification* is this row; the tool that realises it is not.
- **A styled e-commerce product photograph** — rejected. It has real EXIF and a real object, exactly
  like the appearance-model review photo; neither activates on being a photograph.

## The collision fixture

**`Moodboard_Nordic-Minimal.pdf`** — one PDF page: a grid of photographs of other companies'
products, materials and interiors, with a strip of colour swatches down one edge. It looks more like
this row's evidence than anything else on a designer's disk: visual, deliberate, swatched, and made
by the designer as part of the project.

It is not this row's evidence. The discriminator is the **binding**, absent four times over: no
identified part, no named variant that will be produced, no material or finish attached to any
swatch, and no approval or master reference. A CMF specification binds a named appearance variant of
an identified part to a colour standard, a material, a process and a gloss level, and someone signs
it. A mood board collects other people's images and binds nothing.

Routing: **Reference Clips** — 00: "Reference Clips may live under Personal/Reference Clips and hold
saved visual inspiration, product references, quotes, recipes, short article captures, code
snippets, or other material that is useful for later retrieval but does not belong to a current
project." It also carries `group_without_copying_facts: true`, so it may sit in the project's
neighbourhood without acquiring `design_item` or `colourway`.

## Reciprocal boundaries

Written in both directions in the JSON, each naming the same fixture on both sides.

| Neighbour | This row owns | Neighbour owns | Shared fixture |
|---|---|---|---|
| `engineering.cad-model` | the appearance decision and surface-quality intent | the geometry container as controlled form/fit definition with release identity | `BPA-210_Class-A-Surfaces_RevB.stp` |
| `engineering.material-specification` | material as appearance carrier, inseparable from colour/texture/gloss | material as performance: grade, strength, compliance | `MT-11020_Texture-Application_…pdf` vs a resin datasheet for the same shell |
| `engineering.prototype-build` | appearance models that represent look and explicitly not function | configuration and functional deviation of a built article | one article that is both carries both records |
| `creative.graphic-design-project` | colour standard bound to a moulded/finished part | colour standard bound to ink on a substrate | `Packaging_Dieline_Pantone-2985C.ai` |
| `creative.uiux-product-design` | physical form, colour, material, finish | screens, flows, components, interaction states | a device render composited with a screen mockup |
| `manufacturing.supplier-qualification` | the document that **establishes** the appearance standard | the submission demonstrating **conformance to** it | the PPAP AAR cites the master-sample approval |
| `business_operations.user-research` | human-factors studies constraining a named item's form | discovery whose object is a need or behaviour, no design item | `Grip-Study_Handheld-Rig_Reach-Envelope.pdf` |
| `research` | an identified item's appearance | generalizable knowledge, by project/stage/artifact/lab/venue | the same grip study, when written for publication |

`role_split → manufacturing.inspection-record`: one master sample, two roles — approved appearance
standard here, acceptance limit there. The sample identifier alone activates neither.

## Neighbours considered that got no edge

- **`code`** (named in the assignment) — nothing here is a repository. Rendering scenes and material
  definitions are assets, not source; a render farm's job scripts activate `code` on repository
  evidence with no appearance binding. The engineering↔code collision is about firmware and does not
  reach the appearance seam.
- **`manufacturing`** at schema level — the collision is written against the row that actually
  competes (`supplier-qualification`) plus a schema-level `also_holds_with`; both would double-count.
- **`creative.brand-identity`** — close (a brand palette can dictate a colourway) but one step
  removed: the file where it actually collides is the packaging dieline, already covered.
- **`creative.interior-design` / `construction_property`** — the bespoke-fit-out case is real and I
  could not settle it. NJ-IDS-3 rather than a guessed edge.
- **`business_operations.product-requirements`** — a PRD may state an appearance requirement, but a
  requirement is the engineering schema's own territory and that seam is argued there.
- **`photos`** — the review photograph is handled by `group_without_copying_facts: true` plus a
  One-Off Images fallthrough, a stronger answer than an edge.

## Recommendations to R1c (cross-row — not applied here)

1. **The engineering schema row's `also_holds_with` should probably include `creative`.** ID
   co-activates with creative work genuinely and often. Because a template may not widen its
   schema's set, every such file is currently forced to be a *collision* — correct under the
   contract, possibly the wrong model of reality. Raised as NJ-IDS-2; nothing widened unilaterally.
2. **Adjudicate `colourway` together with `revision_or_baseline`.** They are two halves of one
   question — whether the system can represent concurrence at all, or only supersession.
3. **If the discipline name in the id worries R1c, rename rather than refuse** — no signal,
   dimension or privacy rule depends on the words "industrial design".

## proposed_fields justification

One key: `colourway`, string, `validated`, adjudicate R1c. No canonical key names a concurrent
appearance variant; `version_family` and the schema's proposed `revision_or_baseline` both encode
supersession and a colourway is explicitly not superseded; `design_item` names the item, and folding
a variant into it would make one product read as three; `artifact_type` / `engineering_artifact_type`
/ `work_type` name kinds of document, not which variant a document governs. The ceiling is
`validated` because a bare colour word in a filename is far more often a beach than a colourway and
needs a co-occurring standard/material/finish binding for the same part. No regex, no threshold, no
gazetteer content — R2 and R4 own those. `fields` is `[]` per PR-6; no canonical key was minted or
re-declared.

## NEEDS-JOSEPH

- **NJ-IDS-1** — is `colourway` a destination-eligible key, a value of `engineering_artifact_type`,
  or search-only? (a) destination key as recommended — costs one proposed key and needs the
  single-variant collapse rule; (b) enum value — costs nothing but loses the ability to group a
  render, a CMF row, a master sample and an approval as one variant, this row's main grouping
  reason; (c) search-only — safest, but the third dimension reverts to `lifecycle_stage` and leg 2
  weakens to signals-plus-privacy only.
- **NJ-IDS-2** — add `creative` to the engineering schema's `also_holds_with`, or keep adjudicating
  every design/creative overlap as a collision? See recommendation 1.
- **NJ-IDS-3** — a bespoke interior fit-out or facade element has appearance, colour, material and
  finish, and a mock-up panel that behaves exactly like a master sample, but is not a reproducible
  product. This row (keeps the CMF machinery, strains "product"), `creative.interior-design`
  (natural fit, no appearance-approval machinery), or `construction_property` (owns site and
  instruction, treats appearance as a specification clause)? Not guessed.
- **NJ-IDS-4** — should a **concurrent-sibling** relation (option set, variant family) exist,
  distinct from `version_family`'s supersession? This row needs it twice: for downselect option sets
  and for colourways. Alternatives: a new grouping relation; overload `version_family` and accept
  that "later" becomes meaningless inside it; or leave option sets unstructured and lose the
  downselect as a retrievable fact.

## Self-verification

- `python3 -m json.tool` parses the JSON.
- Every `source_type` used is a member of `SOURCE_TYPES` (checked mechanically, examples and
  `file_kinds` both).
- All five `design_cite` strings were grepped out of `00` verbatim before being written; no other
  quotation marks anywhere in either file are attributed to `00`.
- Every edge endpoint resolves on `roster.json` (checked mechanically, zero missing):
  `engineering.cad-model`, `engineering.material-specification`, `engineering.prototype-build`,
  `creative.graphic-design-project`, `creative.uiux-product-design`,
  `manufacturing.supplier-qualification`, `business_operations.user-research`, `research`,
  `manufacturing`, `business_operations`, `manufacturing.inspection-record`. Five residual names are
  §7.3 names.
- `also_holds_with` (`manufacturing`, `research`, `business_operations`) is a strict subset of the
  engineering schema row's declared set, and no `also_schema` on any file example names a schema
  outside it — which is why the packaging dieline is `null` and a collision instead.
- `fields: []`; one `proposed_fields` entry; no canonical key re-declared or synonymised.
- No threshold, confidence score, handling class, or folder path written as a fact.
- Twelve file examples, observations split from facts throughout, two with
  `group_without_copying_facts: true`.
- `never_alone` clauses that a tempting false file trips: the colour-standard-token clause stops
  `Packaging_Dieline_Pantone-2985C.ai`; the mood-board clause stops the collision fixture.
- Files written: exactly the two assigned. No neighbour node, roster, `canonical_fields.json`,
  `check.py`, `src/` or SPEC touched, and `planning/29-DOMAIN-OWNERSHIP.md` was not edited.
