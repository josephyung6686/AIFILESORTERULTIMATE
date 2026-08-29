# engineering.simulation-analysis — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.simulation-analysis.json`](engineering.simulation-analysis.json).
Salvage: none — no prior JSON or memo existed for this id. Both files are new.
Verdict: **node kept**, narrowed to the deck-and-idealisation relation, with the report conceded as
a shared fixture with its own schema's default template.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped assignment
  (`make_prompt.py engineering.simulation-analysis`) — the six depth requirements, the node test,
  the output shape, the done-when list.
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted grep only. Seven
  spans were matched with `grep -F` verbatim before use; four are quoted in the node.
- `planning/domains/nodes/engineering.json` — the schema anchor. Read for its default template
  (`project → design_item → lifecycle_stage → engineering_artifact_type`, `time_first: false`), its
  ten deterministic signals, ten `never_alone` rules, four proposed keys, `work_types[]`, declared
  `also_holds_with` set, and sensitivity reason. All three legs are measured against it, and this
  row concedes one of its twelve file examples.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the depth calibration named in the
  brief. Its idiom is followed directly: the argued `role_split` refusal, the neighbours-without-
  an-edge section, and the discipline of parking a tempting key rather than minting it.
- `planning/domains/nodes/engineering.cad-model.json`,
  `engineering.civil-structural.json`, `engineering.invention-disclosure.research.md` — the three
  landed rows that already argued a boundary against this id (found by one grep). The first two are
  quoted and reciprocated on the same fixture bytes; the third makes the strongest case *against*
  this row and is answered head-on below. None was edited.
- `planning/domains/roster.json` (all 16 edge endpoints checked mechanically) and
  `planning/domains/canonical_fields.json` (37 keys; `study_type`, `load_case`, `analysis_type` and
  `solver` are all absent, which is the argument for the one proposal made).

## THE CHARGE — the strongest case that this row should not exist

Stated in full before anything was written, because on this id the case is genuinely strong and a
landed neighbour has already made part of it.

1. **It is a `work_type` value.** The engineering schema's own `work_types[]` contains
   `"analysis model or calculation"` and `"simulation report"`. The brief and ALIGNMENT are
   explicit that work types are values of a field and never nodes. On its face this id is
   `engineering_artifact_type = "simulation report"` with a folder around it.
2. **It is a duplicate of its own schema's default template.**
   `engineering.invention-disclosure.research.md` says of this id and
   `engineering.requirements-specification`: *"Both are the schema default's home ground and
   neither produces inventorship, claim or office structure."* And the schema's deterministic list
   already contains an analysis clause — an analysis package whose labelled inputs include a
   model/configuration identifier and whose conclusion compares calculated margins or performance
   against named requirements for that same item. If the default already fires on this evidence,
   CONNECTION.md's node test says refuse.
3. **It is a document type.** "The FEA report" is a document-type word in exactly the class of
   "the invoice" or "the certificate".
4. **It is a tool row and a file-format row wearing a discipline's name.** FEA and CFD are software
   categories; the id's real content risks being `.inp`, `.odb`, `.cas`, `.nas`, `.rst`. `00` is
   explicit that the engine should *"treat the file extension as a routing signal rather than an
   assumption about meaning"*.
5. **It is a lifecycle stage** — the phase between design and test — which is a value of the
   schema's own proposed `lifecycle_stage`, not a filing world.

### How the charge was defeated, and where it was conceded

Charges 1, 3, 4 and 5 fall to the same fact: **this row's evidence is not a word, a type or an
extension but a relation the schema default never names** — an *idealisation* joined to a *load
case* joined to a *run* joined to a *post-processed answer*. Three of the four members of that
relation carry it with no type word and no report anywhere:

- `BPA-210_Static_LC3_v04.inp` carries it in ASCII with no title block, no approval slot and no
  revision table — nothing the default keys on is present, and the file is unambiguously this row's.
- `BPA-210_mesh_1p5mm.nas` carries the idealisation alone: GRID and element cards, stem matching an
  as-designed container, and *visibly different geometry* — fillets and fastener holes absent.
- `Mesh-Convergence-Study_intake-duct.xlsx` is a table whose subject is *the reliability of its own
  numbers*. No other row on this schema, and none on any neighbouring schema, produces that.

Charge 2 is the serious one and is defeated **narrowly and reciprocally, not broadly.** The schema
default genuinely owns the *conclusion* of a study report — that is precisely what its analysis
clause describes, and it lists `BPA-210_FEA_Loadcase-3_RevA.pdf` as one of its own twelve file
examples. So this row does **not** claim exclusivity over it: the fixture is carried here with a
`must_not_conclude` line saying so in words. What the default is blind to is the deck, the mesh,
the result container and the convergence evidence — which are the majority of the bytes and the
whole of the retrieval problem, and which are held by no neighbour either. Two landed siblings had
already routed exactly that material here before this row was written:

- `engineering.cad-model`: *"This row owns the as-designed geometry; simulation-analysis owns the
  defeatured, meshed, load-and-boundary-condition model and the study that produced it."*
- `engineering.civil-structural`: *"That row's relation is a numerical simulation run: model, mesh,
  solver, load case, post-processed result. […] a mesh convergence study is only theirs."*

The row is narrowed to what those two sentences describe. The tool reading, the extension reading
and the word reading are each written into `never_alone` so the node cannot activate on them, and
the name was changed from the assignment's discipline label ("Simulation, FEA and CFD studies") to
the situation ("Simulation studies and their solver models") for the same reason
`engineering.civil-structural` renamed itself off its discipline.

## The node test, all three legs

**LEG 1 — signals differ. YES.** The schema default recognises a controlled definition by
*approval apparatus*: title block with revision and approval slot; requirement rows with allocation
and verification-method columns; a design-authoritative BOM parent/child relation; a TDP manifest;
an ECR naming an affected item; a verification matrix binding requirement ids to a
configuration-under-test. Every one of those structures says **somebody signed this**. This row's
four structures say **somebody computed this, and the answer is only as good as the idealisation**:
(a) discretisation cards co-occurring with material, boundary-condition and load/step cards; (b) a
case dictionary joining a solver application, a mesh spec, BC patches and run control for one named
geometry; (c) a report section chain of idealisation → mesh → materials-with-source → BCs and load
cases → results → margin; (d) a table whose independent variable is element or cell count and whose
dependent variable is the answer. None is in the default's list. The default's nearest clause
reaches only (c), and reaches it by its conclusion.

**LEG 2 — dimensions differ. CONDITIONAL, and written as conditional.** PR-6 forbids declared
fields, so `dimension_order` is `[]` here exactly as on the schema row. The researched difference,
exposed for R1c: the default's `lifecycle_stage` **does not partition this corpus** — one item
accumulates a static, a modal, a thermal and a drop study inside one gate, while the same load case
is rerun at every gate, so a gate level scatters one study's rerun history and merges four
unrelated physics. And `engineering_artifact_type` **collapses to a single value** across the whole
corpus and opens a folder with one child. The researched order is
`project → design_item → study_type → (deck | model | result | report)`. Three optional branches are
recorded: a `load_case` leaf where a single-valued labelled slot exists; `study_type` omitted for a
single-physics corpus (returning to the default); and no `design_item` level for a methods or
benchmark corpus, which should more often fall through than be filed.

**LEG 3 — privacy reason differs. YES.** The schema default's reason is proprietary design
definition, supplier data and export control — commercial confidentiality. This row's reason is
different in kind: a simulation result is a written statement of *how, where and at what load a
product fails*. Peak stress locations, fatigue life, thermal runaway onset, crash and
occupant-injury predictions, blast response. An adverse margin is the most discoverable artifact an
engineering organisation holds and it describes a hazard to third parties. Case archives
additionally carry solver licence files and cluster credentials that are not design content at all
— `SIM_BPA-210_Baseline-C.zip`'s manifest lists both. Value stays `potentially_sensitive`; no
handling class is assigned.

## The collision fixture

**`LOT-24-081_Cpk-Study.xlsx`** — a manufacturing process-capability study. It carries the word
*Study* in its filename, a histogram, upper and lower specification limits, an index that reads
exactly like a margin, a pass verdict, and it lives in the same organisation's folders under the
same item's program. Everything about its surface says this row.

The discriminator is **the input, not the output**: its numbers come from *measured parts* out of a
lot, with a measurement-device reference. There is no mesh, no boundary condition, no material
model, no load case and no solver. Its `facts_legal` is empty and it routes to `Independent
Records`. `manufacturing.inspection-record` owns it unconditionally and this row takes nothing from
it.

A second collision fixture was kept because it attacks a different surface:
**`monte_carlo_npv_simulation.xlsx`** shares this row's *entire vocabulary* — simulation, run,
trials, iterations, convergence, distribution — and none of its structure. It is
`business_operations.budget-forecast`'s, and it is the reason the word *simulation* heads
`never_alone`.

## Files considered and rejected

- **A solver licence file, an installer, a tutorial dataset, a training deck.** All carry the
  vendor name that is this world's most conspicuous string. Each would have made the node a tool
  row, which is the charge it had to defeat. The licence file survives only as a *member* of the
  archive manifest, and only as a sensitivity fact.
- **A raw geometry point cloud / STL with no siblings.** Discretised geometry with no material, BC
  or load evidence anywhere. Correct outcome is abstention, and it is written into `never_alone`.
- **A published validation benchmark case** (a standard's lid-driven-cavity or NAFEMS-style
  problem). No design item, and its object is a proposition. `research.dataset-analysis`.
- **A material datasheet.** It supplies a material card's values, but a datasheet alone is a
  reference document; it is `Independent Records` or `engineering.material-specification`.
- **A cluster job scheduler log / `slurm-4471.out`.** Machine state, not a record of a study. It is
  `filesystem`-level noise; adding it would have made this a devops row.
- **An ML training run** (`loss_curve.png`, a checkpoint, a sweep config). Genuinely the hardest
  rejection: "model", "run", "convergence", "residual", "parameter sweep" are shared word-for-word.
  Rejected because there is no physical quantity, no idealisation and no design item.
  `code.notebooks-experiments` / `research.dataset-analysis`.
- **A digital-twin telemetry stream.** A simulation-adjacent phrase whose actual bytes are sensor
  time series from a real asset — `manufacturing.asset-register` territory.
- **A CAE marketing PDF or webinar recording.** Contour images and physics words with no study.
  `Reading Inbox` or `Reference Clips`.

## Reciprocal boundaries — both directions, same fixture

| Neighbour | Fixture named on both sides | Their side | This side |
|---|---|---|---|
| `engineering.cad-model` (they wrote first) | `BPA-210-001_RevC.STEP`; `BPA-210_mesh_1p5mm.nas` | as-designed geometry; the STEP is theirs | the STEP is mine **only** as a named input recorded inside a study; the mesh is mine despite the shared stem |
| `engineering.civil-structural` (they wrote first) | `Wind-Loading-ASCE7-22_Calc.xlsm`; a mesh convergence study | compliance: demand vs capacity against a cited published clause for a fixed work | the numerical run: model, mesh, solver, load case, result. A frame FE model feeding member checks sits in both |
| `engineering.verification-validation` | `Simulation-Model-Validation_DVT07-vs-FEA.xlsx` | the physical article: requirement id, method, procedure, configuration-under-test, measured result | the computation: idealisation, mesh, BCs, load case, run, predicted result. Disjoint columns; neither copies across the error column |
| `engineering.requirements-specification` | `BPA-210_FEA_Loadcase-3_RevA.pdf` citing `SYS-REQ-042` | rows of stable requirement ids with allocation/rationale/verification-method columns | a computed answer that *cites* one. A citation is not a declaration, in either direction |
| `engineering.process-plant-design` | a flowsheet with a stream table | unit ops, streams, component lists, mass and energy balance — a simulation with no mesh | CFD of one vessel's internals inside the same package |
| `manufacturing.inspection-record` | `LOT-24-081_Cpk-Study.xlsx` | theirs unconditionally — measured parts, device reference | nothing; this row concedes it entirely |
| `code.software-project` | `controlDict` and its case tree under git | repository root, manifest, test suite, source structure | solver application + BC fields + mesh spec for a named geometry. **Both hold** |
| `research.dataset-analysis` | a material-model parameter sweep with error analysis | object is a proposition; venue, citations, generalisable claim | object is a named item's behaviour under a stated load case |
| `creative.3d-asset` | a cloth/smoke/rigid-body cache beside a scene file | a solve whose output is an image sequence — scene graph, lights, render setup | a solve whose output is a number compared against a requirement |
| `engineering.stage-gate-review` | `CFD_intake-duct_report_2026-05-02.pptx` | decisions, actions, exit criteria, attendance | idealisation, mesh, BCs, results. A review pack that merely embeds a contour is theirs |

`engineering.risk-analysis-fmea`, `manufacturing.failure-analysis` and
`business_operations.budget-forecast` carry the same treatment in the JSON.

## Neighbours considered that did **not** get an edge

- **`engineering.change-order`** — a study is the most common *justification attached to* an ECR,
  but the ECR's structure (affected item, current/replacement revision, disposition) never appears
  in a study and vice versa. Same-evidence confusion does not arise; the fixture never sits between
  them.
- **`engineering.aerospace-airworthiness` / `engineering.automotive-program`** — both consume
  analysis as certification or program evidence, but the discriminating structure on those rows is
  a regulatory or program apparatus this row's files do not carry. Adding edges would give one
  evidence item three claimants.
- **`engineering.electrical-schematic` / `engineering.pcb-layout`** — signal-integrity and thermal
  simulation of a board is real and is listed as a `study_type` value, but the shared fixture is
  already governed by the `engineering.cad-model` and code edges. A third statement of the same
  seam is duplication.
- **`engineering.drawing-package`** — no shared discriminating evidence. A study never carries a
  sheet register and a package never carries a load case.
- **`manufacturing.warranty-claim`** — the failure-analysis edge already covers the seam.
- **`role_split`** — **empty, and this is the interesting refusal.** The split this world most
  wants is *predicted* against *measured* behaviour of one item: this row versus
  `engineering.verification-validation`. It is not a `role_split`, because a `role_split` requires
  the two sides to carry **different field keys** for the same entity, and both sides would carry
  the same `design_item`. There is no canonical predicting-versus-measuring key, and minting one to
  serve a single template is the move the crypto row named as the overnight pass's failure. The
  seam is expressed as a collision with the disjoint-columns rule in the fixture's
  `must_not_conclude`.

## Fields and `proposed_fields`

`fields: []` by PR-6 and by the contract rule that a template references its schema's fields and
never copies them. The legal set on a recognised file is whatever R1c licenses on the engineering
schema — its proposals `project`, `design_item`, `lifecycle_stage`, `engineering_artifact_type`,
`revision_or_baseline` — plus the six universals.

**One key proposed: `study_type`** (enum, `linear static structural`, destination-eligible,
`reliability_ceiling: validated`; full argument in the node). It is proposed because it is the only
thing that makes this row not the default: no canonical key names the physics a computation
asserts. `engineering_artifact_type` is orthogonal, not synonymous — it separates a drawing from a
calculation, and on this corpus resolves to one value for every file. Canonical `artifact_type` is
research/code and its `model` value means a trained or analytical model, not an idealisation with
boundary conditions; `work_type` is academic; `stage` is a research workflow position;
`lifecycle_stage` is a gate.

Deliberately **not** proposed: **`load_case`** — the more obvious candidate and the fact users
actually name, refused because one linear static run routinely sweeps a matrix of load combinations,
so the fact is multi-valued per file and can never be a destination dimension (the identical
objection `engineering.civil-structural` used to refuse `design_code`); parked as NJ-SIM-2.
**`solver`** — a vendor string, and making it a key would make a tool the organising principle,
which is this row's own charge against itself. **`mesh_size`** — a parameter, not a fact about what
a file is. No variant of the schema's four unadjudicated keys was minted.

## Sparse-file discipline

`run_042_convergence.png` is this node's `HW 3.pdf`: a decreasing curve against an iteration axis,
axis labels only, no EXIF, sitting beside two accepted files. It is
`group_without_copying_facts: true`, its `facts_legal` is universals plus `media_type`, and its
`must_not_conclude` says in words that the neighbourhood groups it and supplies it nothing — and
that a decreasing residual is equally a training loss or an optimisation objective. `.odb` and
`BPA-210_mesh_1p5mm.nas` carry the same flag for the same reason: a matching stem is a grouping
relation, never a copied fact.

## One contract correction made during writing

`Screenshot 2026-05-02 at 14.11.07.png` was initially given `also_schema: "photos"`. Set to `null`:
`photos` is **not** in the engineering schema row's declared `also_holds_with` set (`manufacturing`,
`code`, `research`, `business_operations`, `construction_property`), and a template must not widen
its schema's co-activation edges. The photos-side outcome is expressed where it belongs — the
`Temporary Screenshots` residual route. Same defect the crypto memo recorded and corrected; noted
so R1c can see the pattern being caught rather than repeated.

## Audits run before returning

`json.tool` parses. All 16 edge endpoints (13 `collides_with`, 3 `also_holds_with`) resolve to
`roster.json` `domain_id`s. All 14 `file_examples.source_type` and 11 `file_kinds.source_types`
values are in the fourteen-member `SOURCE_TYPES` list. All 5 `falls_through_to` names and all 14
`falls_through_if_inactive` names are among `00`'s nine residuals. All 7 candidate `00` spans
matched with `grep -F` verbatim, em-dashes included; **no `00` quotation here is fabricated or
paraphrased inside quote marks**, and the neighbour quotations were copied from those files' own
text. `fields: []`, one `proposed_fields` entry, `dimension_order: []` per PR-6, `role_split` empty
with an argued note. No threshold, score, evidence count or handling class appears in either file —
the digits present are fixture names, dates and mesh sizes inside fixture names. Only the two
assigned files were written; no neighbour, roster, canonical-fields, `check.py`, `src/` or SPEC
file was touched.

## NEEDS-JOSEPH (this node only)

- **NJ-SIM-1 — is `study_type` a new key, or a widening of `engineering_artifact_type`?** Widening
  gives one key two orthogonal jobs and makes a deck and a report indistinguishable at the level
  meant to distinguish them; a new key adds a fifth unadjudicated engineering proposal to the four
  already before R1c. Preference stated (new key), reason stated (orthogonality). Mirrors NJ-ENG-1
  on the schema row — the same question reaching R1c from a second direction is itself evidence
  that the engineering key table needs one decision, not four.
- **NJ-SIM-2 — what is `load_case`?** The fact people name a study by, and multi-valued per file,
  so it cannot be a destination dimension. (a) search-only fact, never a level — current
  recommendation; (b) a leaf where a single-valued labelled slot exists — the template's optional
  branch (a); (c) nothing, left as an observation.
- **NJ-SIM-3 — does a rerun belong in `version_family`?** A rerun with a changed material property
  supersedes its predecessor, but a baseline can contain many artifacts at different revisions and
  `version_family` deliberately does not state which member is current. Mirror of NJ-ENG-2: is
  superseding-by-rerun a relation `version_family` can carry, or a distinct one?
- **NJ-SIM-4 — dual activation on a correlation document.** Where one document holds a physical
  test and its correlated model, this row recommends `engineering.verification-validation` and this
  row both hold on disjoint evidence, no fact crossing the error column. Confirm, or make one side
  primary — the choice decides whether a model's mesh facts can ever be reached from a test report,
  which is the retrieval question this corpus is actually asked.
