# engineering.prototype-build — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.prototype-build.json`](engineering.prototype-build.json). No prior draft existed.

## Sources actually used

`RESEARCH-BRIEF.md`; the stamped assignment from `make_prompt.py`;
`planning/00-database-agent-product-design.md` (targeted grep only — four residual definitions
extracted and verified verbatim); `planning/domains/nodes/engineering.json`, the schema anchor,
read in full because it is what this row is measured against; `roster.json` for every edge
endpoint; `src/evidence_shape/vocabulary.py` for `SOURCE_TYPES`;
`finance.crypto-assets.research.md` as the depth calibration named by the brief;
`engineering.cad-model.json` for the landed key set and house argument shape on a placeholder
engineering template.

Neighbour claims already made **against** this id, found with one grep and read at their matched
lines: `engineering.cad-model`, `engineering.pcb-layout`, `engineering.industrial-design`,
`engineering.invention-disclosure`, and `engineering.automotive-program` (a refusal that routes
mule and prototype coverage here). Four landed rows had cut a hole in the shape of this node
before it was written; every one of those edges is reciprocated in the JSON **using the fixture
bytes the neighbour itself named**.

## THE CHARGE — the strongest case that this row should not exist

1. **It is a lifecycle stage.** The schema proposes `lifecycle_stage` = concept, preliminary
   design, detailed design, qualification, released. *Prototype* sits between the third and
   fourth. A row named for a stage is a named failure mode.
2. **It is a work-type value.** The schema row's own `work_types` list contains the literal string
   `prototype configuration record`. Values are not nodes.
3. **It is a duplicate of its own schema's default template.** The schema's eighth deterministic
   signal reads, verbatim from `engineering.json`, *"a prototype/build record that names the
   experimental article or prototype configuration and reconciles its deviations against the
   intended design definition."* The default already sees this material — which is precisely the
   finding that refused `engineering.automotive-program`.
4. **Half the row's name is a process, a medium and a file format.** "Additive manufacturing" is a
   fabrication process, "print job" a medium, `.gcode`/`.3mf`/`.nc` extensions. None is a filing
   world, and `00` forbids extension as meaning.
5. **It is a duplicate of a neighbour** — a build record is a production record with a quantity of
   one, and `manufacturing.production-record` exists.

Limbs 2 and 3 are the serious ones. Had limb 3 survived I would have refused.

## Why the charge fails — the node test, three legs

### Leg 1 — signals differ by *seeing what the default cannot see*

The refutation of limb 3 is not that the schema's prototype bullet is vague. It is that all ten of
the schema's deterministic signals are **type-level, definition-side** relations among labelled
slots inside one controlled document — title block joined to item and revision, requirement rows
beside verification columns, a TDP manifest, a change block with an affected item, a BOM
parent/child tree, analysis inputs against requirements, a verification matrix. Each describes a
**class** of product.

This row's relation is **token-level and process-side**: an article-identity slot (unit, serial,
build, plate number) bound to a machine identity, a material identity resolved to a lot or spool,
the parameters *actually used* rather than specified, and an **outcome** — completed, aborted,
scrapped, reworked — with a departure list against a named revision. The schema's bullet names the
first and last of those five and never names the process side at all, which is exactly the half
that collides with manufacturing rather than with the definition rows.

That alone is a refinement, and a refinement is not a node. The decisive argument is a fact about
the file list: an ordinary part of this corpus contains **no** title block, **no** requirement
identifier, **no** revision slot, **no** BOM, **no** approval block, and often no item identifier
more formal than `bracket_v3`. `bracket_v3_0.20mm_PETG-CF_MK4.gcode`, `bracket_v3.3mf`,
`Printer-log_2026-03-09_thermal-runaway.txt` and `IMG_4471.jpg` are four of thirteen fixtures,
they are what a maker's disk actually holds, and **the engineering default template cannot fire on
any of them.** This signal set is not a narrowing of the default's; it includes a class of
evidence the default is structurally blind to. Limb 3 fails there.

Limb 1 falls with it: a lifecycle stage is a property of a *definition* moving through gates; an
article with a serial number is an object, and it persists after the definition has moved on.
Limb 4 falls because the row is not defined by process or extension — a CNC first article, a board
spin, a breadboard, an automotive mule and a resin print are one relation at different scales,
`.gcode` is in `never_alone`, and the downloaded-model fixture exists to prove the extension
proves nothing.

### Leg 2 — the dimension order differs by *adding a level the schema has no key for*

Schema default: `project → design_item → lifecycle_stage → engineering_artifact_type`.
This row: `design_item → build_event`.

- `lifecycle_stage` **dropped** — every member of a build corpus sits at one lifecycle point by
  construction; a level with one child is not a level.
- `engineering_artifact_type` **dropped from the standing levels** — within one build the log, the
  deviation list, the photographs, the machine program and the shakedown sheet are *members of a
  single event*. Splitting on type first scatters one build across five folders and makes each
  fragment unintelligible: `00`'s parent-makes-child-intelligible rule applied to a build instead
  of a course. It survives only as an optional leaf **inside** a build.
- `project` **dropped from the front** for the reason the schema row itself gives: a project name
  alone is `business_operations` evidence.
- `build_event` **added** — token-level, where the schema is type-level. No canonical key and no
  key on the schema's own proposal can carry it.

So the order differs in kind, not sort order. Two optional branches are recorded in the JSON: a
machine level replacing `build_event` for a maker corpus genuinely organised by printer (a real
preference, a poor default, since it files by tool); and no `build_event` level where only one
article was ever made — which collapses to `cad-model`'s order and is the honest failure case in
NJ-PB-1. `time_first: false`: a build's date is strong evidence, but `00`'s document-domain rule
puts project/function/subject before time, and date-ordering separates a unit's log from
photographs of the same unit taken a week later.

### Leg 3 — privacy differs weakly, and the row does not rest on it

Stated honestly rather than inflated into a third pillar. The schema is already
`potentially_sensitive` and no handling class is assigned. The one real difference in kind: a
build corpus is saturated with **photographs taken where the work happens**, carrying EXIF capture
time and GPS that frequently resolve to a home address, with incidental people in frame. The
definition-side corpus has none of that. Two rules follow that no definition row needs — a
workshop photograph's GPS is never a build fact, and image members route to `One-Off Images`
rather than a document residual. Legs 1 and 2 carry the row.

**Verdict: `refuse_node: false`** — not comfortably. NJ-PB-1(c) is a live path to a later refusal.

## Reciprocal boundaries — both directions, same fixture on both sides

| Neighbour | Theirs | Mine | Shared fixture bytes |
|---|---|---|---|
| `engineering.cad-model` | geometry as a definition | the build event: machine, material, parameters, outcome | `bracket.stl` / `bracket_v3.3mf` — theirs with a native parametric sibling and an item id, mine as a member of a build record naming machine and material |
| `engineering.pcb-layout` | what is to be made: layer/coordinate structure, designator-to-placement join, no unit identity | actual articles, serials, observed departures | `A2409-CTRL_RevD_Fab.zip` theirs, `A2409-CTRL_RevD_FirstArticle_S-N-002.xlsx` beside it mine; adjacency proves nothing either way |
| `engineering.industrial-design` | appearance models representing look and explicitly not function | configuration and functional departure of a built article | a looks-like model record theirs, a works-like rig with a bill of deviations mine; one article that is both carries both |
| `engineering.invention-disclosure` | witnessed conception tied to an invention title, claim or docket | build steps and observed departures | `Lab-notebook_p114_witnessed_2026-02-27.jpg` — a witness signature decides nothing; witnessing is ordinary in both worlds |
| `engineering.verification-validation` | requirement → method → procedure → pass/fail trace | what the article IS: serial, deviations, firmware load, fixture | `BPA-210_DVT-07_Verification-Report.pdf` (the schema's own fixture) — its configuration-under-test annex is mine, its matrix theirs; one report is two groups |
| `engineering.change-order` | affected item, current/replacement revision, approval against the controlled definition | disposition of one article for prototype use only, changing no released document | `BPA-210_Bill-of-Deviations_Unit-004_vs_RevC.pdf` mine; the ECR raised next week to make deviation three permanent is theirs — same content, different object |
| `manufacturing.production-record` | released definition, lot scale, conformance is the purpose | unreleased definition, one article, departures are expected findings | `LOT-24-081_Final-Inspection.xlsx` stays theirs even though its measured-vs-specified rows look exactly like an as-designed/as-built table, because it carries a lot number, acceptance limits and an inspector disposition |
| `manufacturing.nonconformance-capa` | QMS disposition, containment, CAPA reference; a released process failed | the definition is not final yet | the same as-designed/as-built table, split by whether a containment or CAPA reference is present |
| `code.scratch-prototypes` | throwaway repositories: repository roots, manifests, source structure | physical articles | a directory named `prototype-v2` — code's with a package manifest, mine with a machine program, a build sheet and bench photographs |
| `business_operations` | schedule, budget, governance, delivery | the article that was bought and made | `Prototype-Budget-Q1.xlsx` |

Limb 5 of the charge is answered in row seven of that table: the seam is *released vs unreleased
definition* and *conformance vs finding*, which changes the disposition vocabulary on both sides.

`also_holds_with`: `manufacturing` (a pilot article on production tooling built to an unreleased
definition — both structures separately present; a pilot article does not become a lot) and
`research` (an experimental rig that both produces knowledge and is built to a definition, on
`00`'s abstract-that-is-also-an-application-document pattern). The third entry,
`engineering.invention-disclosure`, exists only to mirror a landed sibling and is queried in
NJ-PB-5.

## The collision fixture

`3DBenchy_0.2mm_PETG_MK4.gcode`, in a downloads folder beside eleven unrelated model archives.

It carries **three of this row's four process signals at full strength** — a labelled printer
profile, a material, and a complete parameter block at stock values — and is not a build record of
anything. What discriminates it: **no owned design item, no outcome, no departure, no article
identity** anywhere in it or its neighbourhood. The stem is a widely distributed third-party
benchmark model. The neighbourhood is a download session, and `00` forbids a session as proof of
topic, which kills the last available inference. Routes to `Review Later`, marked
`group_without_copying_facts: true`.

This is why every deterministic signal in the JSON requires **an article identity or an outcome**
in the join, and why `never_alone` lists the parameter block, the machine name and the material
name as three separate entries — each is individually true of this file.

Secondary collisions, each defeating a different inference: `LOT-24-081_Final-Inspection.xlsx`
(measured-vs-specified rows that are manufacturing's), `Prototype-Budget-Q1.xlsx` (the word
alone), `Printer-log_…thermal-runaway.txt` (a machine's afternoon, not an article), `IMG_4471.jpg`
(a photograph whose only link to a build is its neighbourhood).

## Files considered and rejected

- **A supplier quotation for prototype tooling** — a purchase record. Including it would let the
  row activate on procurement language.
- **A PETG-CF material datasheet** — a published property document for a *class* of material;
  `engineering.material-specification`, and the schema already routes standalone datasheets to
  `Independent Records`. A material *lot* is mine; a material *spec* is not.
- **Printer firmware image / vendor installer** — `opaque_binary` software about the machine, not
  about an article. `Unsupported or Encrypted`.
- **A printer maintenance log** (nozzle changes, belt tension, bed levelling) — the closest call.
  It has machine identity, dated entries and outcomes and looks exactly like `Printer-log`.
  Rejected because its object is the **machine's condition**; `manufacturing.maintenance-work-order`
  owns it. The run log is kept instead because a run log is bounded to one *session* and can be
  joined to a build that names it, whereas a maintenance log never can.
- **A calibration cube the user actually made and measured** — genuinely mine, but it teaches
  nothing the build log does not; its useful role is as the near-miss twin of the Benchy.
- **A CAD assembly of the same part** — `engineering.cad-model`'s by that row's own fixture.
  Listing it would be theft dressed as coverage.
- **A test-fixture drawing** — `manufacturing.tooling-fixture`. A fixture makes or holds the
  article; it is not the article.
- **A `.ics` invite for a build review** — a calendar event; `engineering.stage-gate-review`
  already owns the review deck.
- **A product-launch prototype video** — media *about* a prototype. `Reference Clips`; admitting
  it would make this a marketing row.

## Neighbours considered that did **not** get an edge

- **`manufacturing.tooling-fixture`** — jigs and fixtures appear constantly in build photographs,
  but the discriminating evidence never collides: a fixture record's object is the tool. The
  temptation is adjacency, which `never_alone` already refuses.
- **`manufacturing.asset-register`** — the seam is real; recorded in `role_split_note`, below.
- **`engineering.requirements-specification` / `engineering.simulation-analysis`** — upstream of a
  build, sharing no discriminating evidence; the `verification-validation` edge carries the whole
  downstream seam.
- **`photos.*` as a row-level edge** — `IMG_4471.jpg` carries `also_schema: "photos"` at file
  level because the photos schema supplies its capture facts. Promoting that to a row relation
  would make a build row a photo row.
- **`legal.*`** — an export-control or proprietary marking is a *marking*, not an instrument.
  Handled by `sensitivity`.

## `role_split` — empty, and that is a finding

The obvious split is the physical unit: a **built article** here, a **managed asset** in
`manufacturing.asset-register`. One entity, two roles — textbook `role_split`. It is not written
because `role_split` requires the two sides to point at **different field keys**, and under PR-6
this row has no legal key at all; the only candidate on either side is a proposal awaiting R1c.
Writing it now would encode a key relation that does not exist. Recommended to R1c, not asserted.

## `proposed_fields` — exactly one, and the restraint is the point

**`build_event`** (string, `validated`, `destination_eligible: true`, second level only).

No key identifies **one made article**. `design_item` is deliberately type-level — its own
justification says one design item can survive across projects — so overloading it with
`BPA-210 Unit 004` would split an item's requirements, drawings and analyses across every unit
ever built from it. `batch`/`lot` carry manufacturing's released-definition, quantity-many
meaning. `version_family` identifies a family of *files*; two units of one revision are not
versions of each other. `revision_or_baseline` names the definition the article was built to, not
the article.

Everything else this material is drenched in — machine identity, material lot, layer height,
nozzle temperature, feed rate — is deliberately **not** proposed. They are process parameters:
good evidence, legitimate search, catastrophic as folder levels, since a directory named for a
nozzle temperature partitions two adjacent files of the same build. One key, not six.

`proposed_context_terms` are PROPOSED for R6, not design; `00` states the pattern-plus-context
*shape* for course codes only and does not list these. Three of them — `layer height`,
`print profile`, `filament spool` — are listed because their correct outcome on the Benchy fixture
is a **refusal to fire**.

## Sparse-file discipline

Four of thirteen fixtures carry `group_without_copying_facts: true`, which is high and is the
point: this world produces a lot of evidence that is real and nearly anonymous. `IMG_4471.jpg` is
the `HW 3.pdf` of this node — a photograph of a failed print, no text in frame, beside two
accepted build records naming `BPA-210 Unit 004`. Its `facts_legal` is the universals only, and
its `must_not_conclude` covers both halves of `00`'s rule: no `design_item` or `build_event`
copied from neighbours, and no screenshot status inferred from EXIF properties.

## Audits run before returning

`python3 -m json.tool` parses. Key set compared field-by-field against `engineering.cad-model.json`
— identical, with one key added inside `node_test` (`charge_against_the_row`), because burying the
refusal case in a memo would let the JSON read as complacent. All four `00` quotations
substring-verified verbatim against the source before writing, em-dashes included; no other span
in the node is inside quote marks attributed to `00`. All 13 `file_examples.source_type` values in
`SOURCE_TYPES`; all 10 `collides_with`, 3 `also_holds_with` and 3 `also_schema` values resolve
against `roster.json`; all 4 `falls_through_to` names are among `00`'s nine residuals. `fields: []`
per PR-6, no handling class, `sensitivity: potentially_sensitive` only, no threshold, score, count
or regex anywhere. Only the two assigned files written.

## NEEDS-JOSEPH (this node only)

- **NJ-PB-1 — no key names one made article, and leg 2 of the node test depends on it.**
  (a) Mint `build_event` as proposed. (b) Overload `design_item` with `BPA-210 Unit 004` — cheap,
  and it destroys the type-level grouping `design_item` exists to provide. (c) Leave build identity
  as a searchable observation only — in which case this row's order collapses to `design_item`
  alone, becomes indistinguishable from `engineering.cad-model`'s, **leg 2 fails, and this row
  should be refused and folded into `cad-model` plus `verification-validation`.** Stated because
  it is real.
- **NJ-PB-2 — a downloaded third-party model, sliced but never made.** `Review Later` recommended
  (meaning partly understood, location needs a decision). `Independent Records` and a
  reference-collection row are both defensible; `00` does not settle it, and this is a
  high-volume case on a real maker's disk.
- **NJ-PB-3 — is an accepted prototype deviation ever `manufacturing.nonconformance-capa`
  evidence?** Recommended: no, absent a QMS disposition or containment structure. But a regulated
  developer may run prototype departures through the same QMS, in which case one file holds both.
- **NJ-PB-4 — `source_type` routing for `.gcode` / `.nc`.** Treated as `code_structured` (a
  machine program is a program with a labelled header block). `opaque_binary` and `text_document`
  are arguable; `00` does not name the case, and the choice decides which extractor ever reads the
  parameter block that half this row's signals depend on.
- **NJ-PB-5 — same-schema `also_holds_with`.** `engineering.invention-disclosure` lists this row
  in **both** its `collides_with` and its `also_holds_with`. This row mirrors that rather than
  contradict a landed sibling, but the reading used elsewhere is that same-schema co-membership is
  grouping plus collision and never an `also_holds` edge. R1c should rule once and apply it to
  both files; if the stricter reading wins, delete the third `also_holds_with` entry here and its
  counterpart there.

## Recommendations to R1c (cross-row; not made here)

1. Reciprocate this row's `collides_with` on `engineering.verification-validation`,
   `engineering.change-order`, `manufacturing.production-record`,
   `manufacturing.nonconformance-capa` and `code.scratch-prototypes` — five rows that do not yet
   name this id. The other four edges are already reciprocal.
2. Adjudicate `build_event` (NJ-PB-1) before `template.dimension_order` can be filled.
3. Settle NJ-PB-5 globally; it is a contract question, not a template question.
