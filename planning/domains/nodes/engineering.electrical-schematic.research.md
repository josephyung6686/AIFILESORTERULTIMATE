# engineering.electrical-schematic — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.electrical-schematic.json`](engineering.electrical-schematic.json).
Verdict: **`refuse_node: true`.** No salvage — neither output file existed before this pass.

---

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full) and the stamped assignment from
  `make_prompt.py engineering.electrical-schematic`.
- `planning/domains/CONNECTION.md` section 2 — read at source rather than through the brief's
  summary. Two clauses decided this row: the template test (a template row exists only if its
  detection signals, recommended dimensions, or privacy rules differ from its schema's default
  template) and the resolution of "subdomain" (never a third roster kind, never a schema per work
  type, never a schema per file format). Both are paraphrased in the JSON **without quote marks**,
  deliberately: the sentences wrap across lines in the source and a quoted span would not grep back.
- `planning/00-database-agent-product-design.md` — reached by targeted `grep -n`, never streamed.
  Three passages did real work: the extractor-policy paragraph on extensions and design/creative
  formats, the structured-text paragraph on text-bearing files, and the residual-library paragraph
  naming the nine homes. All spans quoted in the JSON are verbatim (audit below).
- `planning/domains/nodes/engineering.json` — my schema anchor and the default template I am
  measured against. Read in full; the most important input to this refusal.
- `planning/domains/nodes/finance.crypto-assets.research.md` — depth calibration, per the brief.
- `planning/domains/nodes/business_operations.organisational-records.json` — refusal shape and key
  set only. My JSON's key set matches it exactly (27 keys; `node_test` absent because refused).
- `planning/domains/roster.json` — all six `collides_with` targets resolve against `nodes[].domain_id`.
- `src/evidence_shape/vocabulary.py` — every `source_type` checked against `SOURCE_TYPES` (10/10).

**Neighbour grep.** `grep -rl "engineering.electrical-schematic" planning/domains/nodes/` returned
nothing. No landed row has argued a boundary against this id, so every boundary below is stated
first from this side and the reciprocal half is a recommendation to R1c.

**External reality checks** (no field, gazetteer, regex or threshold created): KiCad `.kicad_sch` is
S-expression text whose symbol entries carry a `Reference` property and whose nets are named labels,
normally beside a `.kicad_pcb`, a `.kicad_pro` and a `.git` directory. Altium `.SchDoc` and OrCAD
`.DSN` are proprietary compound containers yielding filename and format, not nets. A netlist (`.net`,
IPC-D-356) lists net names each followed by reference-designator/pin pairs and is the *handoff* file
between schematic capture and board layout. Building-services electrical drawings are issued on an
`E-` sheet series with a distribution-board schedule, a revision cloud and an issue stamp.

---

## THE CHARGE — the strongest case that this row should not exist

Stated before anything was written. It is four charges, and three land.

**A — it is a work_type value.** The engineering anchor's `work_types[]` contains the string
`"electrical schematic"`, between `"engineering drawing"` and `"PCB layout"`, and its
`work_types_note` says in terms that these are candidate VALUES of `engineering_artifact_type`, not
child schemas. My id is one element of my own schema's value enumeration. That is not an
interpretation; it is the anchor's literal content.

**B — it is a medium and a list of document types.** The roster hint: "schematic sheets, wiring
diagrams, harnesses and panel drawings." Strip the discipline adjective and what remains is *sheets,
diagrams and drawings* on paper.

**C — it is a file format.** In the corpus that exists on disk, what separates this row from its
siblings is `.sch` / `.kicad_sch` / `.SchDoc` / `.DSN` versus `.brd` / `.step` / `.dwg`. 00 forbids
that inference: the engine should "treat the file extension as a routing signal rather than an
assumption about meaning."

**D — it duplicates its own schema's default template.** Every controlled-definition structure a
schematic package carries — title block with item and revision, product structure, change record,
verification evidence — is already a deterministic signal on the anchor.

### The defence, and why it fails

The one honest defence is **connectivity**. The anchor's ten deterministic signals cover title
blocks, requirement rows, technical data packages, change records, product structures, analyses,
verification matrices, prototype records, archive manifests and folder context — and none fires on a
raw netlist or a raw `.kicad_sch`, which carry no title block, no revision slot and no requirement
identifier. That gap is real. If this row owned it, leg 1 would pass and the disjunctive test would
license the node.

It does not own it, for three independent reasons.

1. **Three or four sibling ids claim the same evidence identically.** `main-board.net` is the
   fixture: a netlist is what schematic capture hands to board layout, so
   `engineering.electrical-schematic` and `engineering.pcb-layout` both claim it in full, and
   `engineering.cad-model` and `engineering.drawing-package` claim the container and sheet forms of
   the same item. Four rows claiming one file is not four boundaries; it is one node with a value field.
2. **For most of the corpus the signal is unreadable.** 00 routes proprietary design formats to the
   design/creative extractor, where "unsupported proprietary formats should be recorded as
   indexed-but-unreadable rather than silently treated as empty." A `.SchDoc` yields no nets. What
   remains is the extension — charge C.
3. **For the readable subset the signal belongs to a neighbour.** A `.kicad_sch` is text-bearing, so
   00 routes it through the structured-text extractor for "Text-bearing files such as Markdown,
   plain text, JSON, CSV, source code, notebooks, and configuration files", and it sits under a
   repository root — `code.software-project`'s deterministic evidence, by 00's own instruction that
   code-related files rely on repository roots and package files.

The defence's only real product is therefore a **recommendation to R1c** — add a connectivity signal
to `engineering.json` — not a node. It is recorded in this row's `recognition.deterministic`, each
entry prefixed "REFUSED ROW — does not activate", so the research survives the id's death without
the id being resurrectable from the JSON alone.

---

## The node test, argued in full

**The default I am measured against.** `engineering.json`: `fields: []`,
`template.dimension_order: []`, `time_first: false`, `sensitivity: potentially_sensitive`, ten
deterministic signals, six `needs_llm` questions, ten `never_alone` rules, and a *conditional*
researched order `project → design_item → lifecycle_stage → engineering_artifact_type` that is
explicitly not encoded because PR-6 leaves the schema with no declared fields.

**Leg 1 — detection signals.** The candidate difference (connectivity) is real, is missing from the
anchor, and is nonetheless not this row's: shared with three sibling ids, unreadable in most of the
corpus, attributed to `code` in the readable part. Every other signal I could name is already on the
anchor. **No difference that belongs to this row.**

**Leg 2 — recommended dimensions.** Cannot differ, structurally rather than by judgement. The
engineering schema declares no field rows (PR-6), so the anchor's `dimension_order` is `[]`, and
`_CONTRACT` rule 8 permits a template to branch only on a field its own schema declares. There is no
order available to differ in. Taking the anchor's conditional order for argument, this row would
recommend that same order with `engineering_artifact_type` **pinned to one value** — a filter, not a
different recommendation, and a row that is a filter on a value is what CONNECTION.md section 2
forbids. **No difference, and none possible.**

**Leg 3 — privacy rules.** Identical, and the identity is the finding. The anchor's
`sensitivity_why` already covers proprietary design definition, supplier data, vulnerabilities,
safety analyses and export-controlled information; a wiring diagram sits inside that envelope at the
same level. The best candidate difference I could construct — that a building's power distribution
drawing is physical-security information — was rejected: nothing in 00 or CONNECTION distinguishes
it, and inventing a privacy rule to save an id is worse than inventing a field. **No difference.**

Two legs cannot differ; the third dissolves into a value and a neighbour's evidence. **Refuse.**

**The escape route** (two labelled roles: a *from* terminal and a *to* terminal) is closed in the
JSON's `refuse_reason` so the file defeats its own resurrection. In short: a from/to pair is two
positions *inside one design item*, not two parties, so naming the relation names the item again;
and the pincer leaves no third branch — with an identified item, issue and approval
(`HarnessB_Wire-List_RevA.csv`) the anchor already fires without this row, and without them
(`PanelA_Terminal-Schedule.xlsx`) it is a build aid that `manufacturing.work-instruction` owns.

---

## Files considered and rejected

For a refusal this is most of the work.

- **`Datasheet_LM2596_Rev-J.pdf`** — kept as a fixture *because* it is rejected. Page one carries a
  typical-application circuit with reference designators and net labels: a schematic by every surface
  test, and a vendor reference document illustrating a part someone else made. The part number is a
  catalogue identifier, not a design item; the manufacturer name is struck by the same role ambiguity
  00 identifies for a university name. Routes to Reading Inbox.
- **`Gerbers_MainBoard_RevC.zip`** — rejected from the list. Its `.gbr`/`.drl` members prove only
  `engineering.pcb-layout`'s side of a boundary this refusal dissolves rather than draws; including
  it would have implied the two rows are separable.
- **`LTspice_buck_converter.asc`** — rejected. Genuinely undecidable between hobby experiment,
  teaching artifact and design analysis, and the analysis case is already the anchor's sixth signal.
- **A PLC ladder-logic program (`.L5X`, `.acd`)** — rejected. Control logic is a program: `code`'s
  evidence with a manufacturing-execution neighbour. Claiming it would make this row a software
  domain by the back door.
- **A cable-tray / containment layout (`.dwg`)** — rejected. A spatial installation drawing for a
  property; `construction_property.drawings-revisions` owns it.
- **An electrical installation condition report / distribution-board test certificate** — the
  sharpest near-miss. Unambiguously electrical, names circuits, and is not design at all: a
  compliance certificate for one property (`construction_property.compliance-certificate`, or
  Independent Records if unattached).
- **An `.ics` invite for a schematic review** — rejected. A `SOURCE_TYPE` and an event; nothing
  fires that the anchor's default would not.

## The collision fixture

**`E-102_Lighting-and-Power-Layout_Rev4_IFC.pdf`.** An electrical schematic sheet on every surface
test — circuit symbols, cable references, distribution-board schedule, revision cloud — and not this
row's evidence. What discriminates it is the title block's **site address joined to an issue status
in a professional instruction lifecycle**: the controlled object is a property, not a reusable design
item, so it is `construction_property.drawings-revisions`. The discipline vocabulary is worthless as
a discriminator, which is the point — the file that looks most like this row's evidence is the one it
must never claim, and what saves it is a relation the engineering schema already keys on.

## Reciprocal boundaries

| Neighbour | From this side | From that side | Shared fixture |
|---|---|---|---|
| `engineering.pcb-layout` | must not claim the netlist as its discriminator — it is the handoff | cannot claim it either, same reason | `main-board.net` |
| `engineering.drawing-package` | a controlled sheet with an item and issue is the anchor's signal, not this row's | must not treat wiring lists as a separate class of associated list | `HarnessB_Wire-List_RevA.csv` |
| `engineering.cad-model` | an EDA project directory is a model container like any other | must not exclude EDA projects on discipline grounds | `power-supply.kicad_sch` |
| `construction_property.drawings-revisions` | circuit symbols are not enough; site address + issue status means hands off | the same conventions on a sheet identifying a reusable product with no site or issue relation are engineering's, and must not be claimed because a consulting practice drew it | `E-102_…_Rev4_IFC.pdf` |
| `manufacturing.work-instruction` | a from/to table with no identified item, issue or approval is a build aid — hands off | the same table joined to an identified assembly with an issue and an approver is design definition, and must not be claimed because someone will wire from it | `PanelA_Terminal-Schedule.xlsx` / `HarnessB_Wire-List_RevA.csv` |
| `code.software-project` | repository roots and manifests are code's evidence; must not claim a directory because its files describe hardware | a repository is not the whole story where an identified item, issue status and approval also appear | `power-supply.kicad_sch` |

The first three are the unusual kind: they **resolve by deleting both rows into the schema's default
template**, not by drawing a line. Each entry says so rather than pretending a seam exists.

**Neighbours that did not get an edge.** `engineering.bill-of-materials` — the shared BOM is real,
but a collision entry would imply both rows should exist; NJ-ELEC-2 handles it as one family
decision. `manufacturing.inspection-record` / `failure-analysis` — an ERC report is generated
design-check output, not production inspection; the anchor's `manufacturing` collision already covers
the pass/fail vocabulary. `research.*` and `business_operations.*` — the anchor already carries both
collisions on exactly the seams that would apply here; restating them would give one evidence item a
third claimant. **`also_holds_with` is empty by contract** (co-activation is a schema-row edge, and a
refused template widening its schema's edges is exactly the seam where a template outgrows its
schema). **`role_split` is empty**: the tempting split is *the practice that drew a sheet* against
*the organisation that owns the design*, both in one title block, and there is no canonical key to
split against — minting one to solve a refused row's problem is the move that produced thousands of
private field names in the overnight pass.

## `proposed_fields` — empty, deliberately

`fields: []` because the engineering schema declares none (PR-6) and a template never copies its
schema's list. `proposed_fields: []` because a refused row must not mint vocabulary. The two strings
this material is saturated with are deliberately not proposed: a **reference designator** (`R12`,
`U3`, `TB1` — the same shape is a spreadsheet cell address, a room or rack label, a standards clause
number and a stock code: evidence, never a key, never a folder level) and a **net name** (a value
inside one item's internal structure; a directory named `VBUS` is a filing system nobody wants). The
one genuine field question — whether the discipline is a value of a widened canonical `artifact_type`
or of a role-specific `engineering_artifact_type` — is already open as NJ-ENG-1 on the anchor and is
not re-proposed here. The eleven `proposed_context_terms` are R6 candidates marked as proposals; 00
states the pattern-plus-context *shape* for course codes only and does not list these.

## Sparse-file discipline

Three of ten fixtures carry `group_without_copying_facts: true`: `Main-Board_RevC.SchDoc` (an
unreadable container that may sit in an accepted design neighbourhood without receiving its item or
revision facts), `ERC_report_2026-05-04.rpt`, and `IMG_4471.jpg`. The last is the `HW 3.pdf` of this
node — a phone photograph of a whiteboard circuit sketch whose only suggestion of a domain is the
folder it sits in. Its `facts_legal` is the universals only and its `must_not_conclude` states both
halves: the graph assembles context and does not copy facts onto sparse files, and the absence of
EXIF is not proof of a screenshot.

## Audits run before returning

- `python3 -m json.tool` — parses.
- All five curly-quoted 00 spans and three inline 00 phrases extracted mechanically and matched
  against 00 under whitespace/curly-quote normalisation: **8/8 verbatim, no fabricated quotation.**
  The two CONNECTION.md sentences are paraphrased without quote marks precisely because they wrap.
- Every `file_examples.source_type` and `file_kinds.source_types` member is in `SOURCE_TYPES`.
- Every `collides_with.domain` resolves to a roster `domain_id` (6/6).
- Every `falls_through_to.residual_template` (5/5) and `falls_through_if_inactive` (10/10) is one of
  00's nine residual names; both `must_consider_residuals` are present.
- `fields`, `proposed_fields`, `work_types`, `also_holds_with`, `role_split` all empty, each with its
  reason stated in the JSON rather than left silent.
- No threshold, score or evidence count anywhere; no handling class; `sensitivity` is
  `potentially_sensitive` only. Key set matches the refusal exemplar exactly.
- Only the two assigned files were written. `planning/29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `engineering.json` and every neighbour node are untouched.

## Recommendations to R1c (cross-row; not made here)

1. **Add a connectivity deterministic signal to `engineering.json`** — the three candidates are in
   this row's `recognition.deterministic`, prefixed so they cannot be mistaken for activation.
2. **Decide the artifact-type family in one operation** — NJ-ELEC-2.
3. **Reciprocate the six boundaries above** into the neighbour rows when they land.

## NEEDS-JOSEPH (this node only)

- **NJ-ELEC-1 — the connectivity signal is real and homeless.** It belongs on the anchor, not on a
  refused template. (a) R1c folds the three recommended signals into `engineering.json` —
  recommended; (b) they are left here and engineering ships blind to netlists and EDA source files
  with no title block; (c) a single narrow *connectivity-evidence* template is built for the subset
  with no controlled-definition structure — rejected here, because that row's discriminator is still
  a file format for the unreadable half.
- **NJ-ELEC-2 — this refusal generalises to four sibling ids, and R1c should say so once.**
  `engineering.electrical-schematic`, `engineering.pcb-layout`, `engineering.cad-model`,
  `engineering.drawing-package` and `engineering.bill-of-materials` are five roster ids whose names
  appear as five VALUES in `engineering.json`'s own `work_types[]`. (a) Retire the family together
  and record the coverage as `engineering_artifact_type` values — recommended; (b) keep them and
  accept that four rows claim `main-board.net` identically; (c) keep exactly one survivor, which
  would be arbitrary. **I refused only my own id** and make no claim on the other four beyond this.
- **NJ-ELEC-3 — building-services electrical design has two true relations.** A consulting practice's
  electrical design for a developer is both a reusable engineered system and site information for one
  property. This row recommends `construction_property.drawings-revisions` on the site-address-plus-
  issue-status evidence, which is *narrower* than the anchor's NJ-ENG-3 (which asks whether all
  site-bound design packages should activate both). Confirm consistency, or let NJ-ENG-3 govern and
  treat this recommendation as superseded.
- **NJ-ELEC-4 — if the refusal is overruled, the row cannot be built as written.** A live template
  needs a `dimension_order`, and no engineering template can have one until PR-6 is lifted for the
  engineering schema and R1c adjudicates `engineering_artifact_type`. Overruling this is a decision
  about PR-6 first and about this id second.
