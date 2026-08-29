# engineering.risk-analysis-fmea — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.risk-analysis-fmea.json`](engineering.risk-analysis-fmea.json). No prior draft existed.
Verdict: **node survives**, on two full legs and one partial. The argument that nearly killed it is first,
because it is the most useful thing in this file.

## Sources

`RESEARCH-BRIEF.md` and the stamped assignment. `00-database-agent-product-design.md` by targeted
`grep -n` only — four paragraphs carried everything (extractor shape, stop rules, dimension
recommendation, residual library); every quoted span was matched back verbatim. **`engineering.json`**,
my schema anchor, is the most load-bearing source here: its `recognition`, `template`, `work_types`,
`file_examples` and proposed keys were extracted mechanically, and my node test is decided by a
property of those arrays. `finance.crypto-assets.research.md` for depth calibration.
`grep -rl "risk-analysis-fmea" planning/domains/nodes/` returned four landed rows that had already
argued against me — `business_operations.risk-register` (both files), `engineering.automotive-program`,
`engineering.bill-of-materials`, `engineering.pcb-layout` — read at matched lines only; two changed what
I wrote. `roster.json` for edge endpoints: this is where `manufacturing.failure-analysis`,
`manufacturing.safety-case` and `engineering.process-plant-design` surfaced, none of which the
assignment's `must_consider_neighbors` (`manufacturing`, `code`, `research`) named, and all three of
which are sharper boundaries than the three it did. `src/evidence_shape/vocabulary.py` for `SOURCE_TYPES`.
Not read: my anchor's `.research.md` — the JSON left nothing undecided, because the deciding fact is an
**absence** in a machine-checkable array.

## THE CHARGE — the strongest case that this row should not exist

Six disqualifiers; two are live.

**1. It is a work_type value. (Live, and nearly fatal.)** `engineering.json`'s `work_types[]` contains
the member `risk analysis or design FMEA`, verbatim, one of eighteen. ALIGNMENT says work types are
values and never nodes, and `engineering.bill-of-materials` **refused** on exactly this, escalating
NJ-BOM-1: *"the engineering.\* sub-roster is one node per work-type value — cad-model, drawing-package,
electrical-schematic, pcb-layout, change-order, material-specification, risk-analysis-fmea,
prototype-build, verification-validation and simulation-analysis are each verbatim members of
engineering.json's work_types[]"*. A sibling names me by id and convicts me in writing.

**Defeated on a checkable asymmetry, not on rhetoric.** Membership is necessary but not sufficient, and
the roster proves it: `bill-of-materials` refused while `pcb-layout` (`refuse_node: false`) survived, both
verbatim members of the same array. So something else decided them — **whether the schema's own default
template already carries the structure and a fixture**:

| | dedicated clause in the anchor's `recognition.deterministic`? | fixture in the anchor's `file_examples`? | verdict |
|---|---|---|---|
| bill-of-materials | yes — *"a BOM or product-structure table with a parent assembly identifier…"* | yes — `BPA-210_Product-Structure.xlsx` | refused: it **was** the default |
| risk-analysis-fmea | **no** — none of ten clauses is a failure enumeration | **no** — none of twelve fixtures is a risk analysis | survives |

The ten clauses are drawing/title block, requirements structure, TDP manifest, engineering change,
BOM/product structure, analysis package, verification matrix, prototype build, archive manifest,
parent-folder context. The twelve fixtures are the SYS-REQ doc, the `.dwg`, the product structure, the
ECR, the FEA report, the DVT report, the PDR deck, the TDP zip, `margin_plot.png`, and three collision
fixtures. No FMEA, no HAZOP, no fault tree, no hazard log — not a clause, not a fixture, not a `needs_llm`
line. My structures are absent from the default, so I am not the default.

Second half of the defeat: the value string names an **artifact**; the researched row is a **situation**.
A worksheet, a guide-word grid, a gate diagram, a living register and a workshop record are five artifact
types sharing one relation — a not-yet-occurred failure enumerated against an identified item or process
step and ranked. No one of them is the row, which is why my own `work_types[]` lists fourteen sub-values.

**2. It is a document type word.** Defeated: the row does not activate on the word. `FMEA`, `HAZOP`,
`FMECA`, `risk`, `hazard`, `severity`, `criticality` are all `never_alone`, and `FMEA_Template_Blank.xlsx`
is the proof of practice — perfect filename, perfect column set, no analysed item, no activation.

**3. It is a lifecycle stage** ("the risk phase"). Defeated and inverted: the defining property is that
it *spans* stages. `Hazard-Log_BPA-210.xlsx` is one file carrying one identifier set across four dated
revisions at four gates — which is why I *delete* `lifecycle_stage` from the order. If the row were a
lifecycle stage that level would be its first dimension, not its deletion.

**4. It duplicates a neighbour.** Two real candidates: `business_operations.risk-register` is
column-for-column identical on the happy fixture, and `manufacturing.failure-analysis` shares failure
modes, causes and corrective actions. Defeated by two discriminators decidable from labelled slots — the
*object in the row* (technical failure mode vs organisational exposure) and the *tense* (hypothesised vs
occurred) — both written reciprocally below.

**5. It is defined by an absence** ("risk is what hasn't happened"). Defeated: the hypothesised failure is
present, enumerated, labelled and ranked — more structure than almost any other engineering artifact. The
absence-defined version would be "engineering files that aren't verification reports"; that is not written.

**6. Organisation name / medium / length / format.** Not live: the evidence is column structure, the
fixtures span spreadsheet, text_document, ocr, email and archive, `.xlsx` alone is `never_alone`, and a
named safety consultancy is `never_alone` under `00`'s role-ambiguity rule.

**Net:** the charge convicted a sibling, and the acquittal rests on one mechanically re-checkable fact
about the anchor JSON rather than on my confidence. If R1c re-runs that extraction and finds a
failure-mode clause I missed, refuse this row and route it to the residuals in `falls_through_to`.
NJ-FMEA-1 asks for that re-run en bloc.

## The node test, all three legs

**Leg 1 — detection signals: DIFFER.** Argued from the absence above. What fills the gap is four
structures, each stated as a relation among labelled slots rather than as a word:

- the **two-state row** — function/failure-mode/effect/cause, prevention and detection controls in
  *separate* columns, and a ranking triple appearing **twice** on the same row (as analysed, then
  re-evaluated after a recommended action). Two ranking states of one row is a structure no other
  engineering artifact has, and it is the sharpest signal on the node.
- the **guide-word grid** — a guide-word column crossed with a process parameter against a named node or
  line reference.
- the **top-event root** — one named undesired event at the root of a gate structure descending to basic
  events. The shape plus the named root is the signal; probability figures are not, and are barred from
  becoming facts.
- the **carried register** — stable hazard identifiers, a state slot, a residual classification, the same
  identifiers carried across revisions of one file.

Plus the **anchor** that separates all four from a corporate register: a header block binding the analysis
to an identified design item *or* a named process step *and* to the revision analysed.

**Leg 2 — dimensions: DIFFER.** The schema default is
`project → design_item → lifecycle_stage → engineering_artifact_type`; mine is
`project → design_item → engineering_artifact_type`. The deletion is evidential: a hazard log is a living
document opened at concept and closed at release, so a gate level cuts one continuous revision series into
gate folders — the defect `00` names when it says *"putting year first scatters related work across
calendar folders"*. `design_item` stays above artifact type because `00` requires that *"a parent
dimension should provide the context required to understand the child"*, and a severity ranking or a
top-event name is unreadable — and unsafe to write — until the analysed item is known.

Honest caveat: **under PR-6 `dimension_order` is empty for this row exactly as for the schema**; both
orders live in prose in a `why`. So leg two is argued at the same standing the schema's default has, not
above it. I did not encode an order to manufacture a difference — `engineering.automotive-program` was
refused partly for a difference that dissolved on inspection, and I would rather this one be inspected.

**Leg 3 — privacy rules: PARTIAL, and the JSON says so.** The sensitivity *value* does not differ: the
anchor is already `potentially_sensitive` and names safety analyses among proprietary design material.
Claiming a difference of degree would be the move automotive-program was refused for ("more of that, not a
different rule"). What differs is a **derivation** rule the schema does not state: in this material the
findings *are* the harm, so no finding may become a name — a severity ranking, top-event phrase,
failure-mode phrase or hazard state must never be a folder level, destination or group label, because a
directory or proposal card carrying it publishes the manufacturer's own worst case. The shape of that rule
is read across from `00`'s Protected Records line — such material *"must not cause filenames or content to
be exposed in model prompts"* — as **inference**, not as a claim that an FMEA is a protected record.
CONNECTION's test is disjunctive: legs one and two carry the node.

## Files considered and rejected

- **A stress or thermal margin report** — the most tempting near-miss, because safety motivates it. It
  computes a quantity for the *intended* condition: the anchor's own analysis clause and
  `engineering.simulation-analysis`'s row. A margin is not a failure mode.
- **A safety data sheet** — hazard vocabulary end to end, and a supplier's published document about a
  substance, not an analysis of anything the user designed.
- **An insurance risk survey of a facility** — scored and hazard-worded; its object is an insurable
  property. Nothing fires that a corporate register would not.
- **An information-security risk assessment** — the most numerically risk-shaped office document outside
  this row. Objects are assets and threats, and there is no technical revision anchor — the same
  discriminator that sends `Risk-Register-Q1-2026.xlsx` away.
- **A machinery CE risk assessment** — genuinely close, kept as a `collides_with` case rather than a
  fixture: where the relation is product-to-regulation-to-authority it is
  `engineering.product-certification`'s. As a fixture it would have let a regulation number look like an
  activator.
- **A HAZOP close-out action list with no worksheet** — indistinguishable from any project action list.
  This is *why* the action-tracking clause requires a post-action re-evaluation referencing the same row
  identifier, not merely an owner and a due date.
- **A reliability / MTBF calculation** — numbers about failure, no enumeration, no ranking triple, no
  controls. The anchor's analysis clause covers it.
- **An `.ics` invite to a HAZOP workshop** — a `SOURCE_TYPE` and an event; treating a meeting title as
  topic evidence is what `00` forbids when it says the system *"should not infer a purpose from their
  filename alone"*.

## The collision fixtures

**`Risk-Register-Q1-2026.xlsx`** — likelihood, impact, computed score, owner, mitigation status. Every
numeric risk signal fires. It is `business_operations.risk-register`. **Discriminator:** the objects in
its rows are supplier insolvency, key-person departure and a schedule slip, and there is no item, process
step or revision anywhere in the file. The column vocabulary is *not* the discriminator — it is frequently
identical to a DFMEA's. The object in the row is.

**`8D_Report_Field-Return-4471.pdf`** — failure modes, root causes, corrective actions, and a citation of
the assembly's DFMEA by name. It is `manufacturing.failure-analysis`. **Discriminator:** an occurrence
identifier in a labelled slot (returned serial, lot, complaint reference, incident date) means the failure
*has happened*. Tense decides it without an LLM whenever that slot is labelled; where it is prose only,
that is a `needs_llm` line rather than a guess.

A third is in the corpus deliberately: **`FMEA_Template_Blank.xlsx`**, the empty form with a perfect
structure — the fixture proving the row activates on populated relations, not on column headers.

## Reciprocal boundaries

Ten `collides_with`, each written in both directions on the same fixture. The three that matter:

- **`business_operations.risk-register`** authored this boundary **one-way** toward me and recorded that
  R1c owed the reciprocal: *"Authored ONE-WAY here for that row's author to write against; R1c owes the
  reciprocal."* This is it, agreeing with their discriminator rather than restating it loosely. Same
  bytes both sides: `Risk-Register-Q1-2026.xlsx` never activates here;
  `DFMEA_Brake-Pedal-Assembly_AIAG-VDA_Rev2.xlsx` never activates there.
- **`manufacturing.failure-analysis`** — prospective vs occurred, fixture `8D_Report_Field-Return-4471.pdf`.
  The two documents cite each other constantly; the rule written on both sides is that **a citation is not
  an anchor**.
- **`engineering.process-plant-design`** — fixture: the P&ID that `HAZOP_Unit-200_Node-12_Worksheet.docx`
  names in its node header. The drawing is theirs; the worksheet analysing deviations on one of its lines
  is mine. The worksheet's `must_not_conclude` forbids deriving `design_item` from the referenced drawing
  number — the concrete form of the boundary rather than a slogan.

The other seven are written the same way: `manufacturing.safety-case` (the argument that cites the
worksheet vs the worksheet), `manufacturing.nonconformance-capa` (an embedded risk grading is a section,
not a document), `engineering.verification-validation` (a detection-control column citing a test vs the
test report), `engineering.change-order` (an ECR quoting an FMEA action vs the analysis that generated
it), `manufacturing.quality-management-system` (a procedure describing *how* to perform a method vs an
analysis *of* something), `engineering.aerospace-airworthiness` (certification relation vs enumeration
relation), `engineering.simulation-analysis` (intended vs failed condition).

`engineering.automotive-program` already wrote its side toward me using
`DFMEA_Brake-Pedal-Assembly_AIAG-VDA_Rev2.xlsx`; I adopted that exact fixture name so the two rows agree
byte for byte. No reciprocal is owed back to a refused node, so it takes no edge from me.

## Neighbours considered that got no edge

**`code`** (named in the assignment) — a fault tree is a graph and a hazard log is a table; a software
FMEA's evidence is still the two-state row. **`research`** (named) — a paper *about* a method has no
analysed item and no revision anchor; nothing here fires on it. **`manufacturing.hse-incident`** —
tempting, but an occupational incident occurred, so the occurrence-identifier rule that sends 8D away
sends it away too; a second edge would restate one discriminator twice.
**`manufacturing.inspection-record`** — a pass/fail table, already never-alone on the anchor.
**`role_split`** — empty, and this is the honest refusal: the split the material wants is the **analysed
item** vs the **analysing organisation** (a HAZOP chaired by an external consultancy puts two
organisation names on page one in different roles, exactly `00`'s university-name ambiguity). There is no
canonical producer-side key, and minting one so a single template can disambiguate a letterhead is what
produced thousands of private field names in the overnight pass. Written into `never_alone` and the
worksheet's `must_not_conclude` instead.

## `proposed_fields` — empty, deliberately

Two keys were tempting and both were rejected rather than parked. **A method key** (FMEA/HAZOP/FTA/LOPA)
is a **value** of the artifact-type role the schema already proposes; minting it ships a synonym for a key
in proposal. **A hazard or failure-mode identifier** is a within-content row identifier, unstable across
analyses, and the moment it became a key the next question is whether it may be a folder level — no, for
the reason in leg three. Both are `never_alone` rules instead.

`fields` is empty by PR-6 and by the rule against a template copying its schema's list. Every
`facts_legal` line therefore names a role **still in proposal** on `engineering.json` (`design_item`,
`lifecycle_stage`, `engineering_artifact_type`, `revision_or_baseline`) plus canonical `project`. That
dependency is stated in `fields_note`, not papered over: if R1c declines a key, those lines change.
`proposed_context_terms` (eighteen) are PROPOSED for R6 — `00` states the pattern-plus-context *shape*
for course codes only and lists none of these; nothing is attributed to it. R2 owns any pattern.

## Sparse-file discipline

Three fixtures carry `group_without_copying_facts: true`, one for each shape `00` warns about.
`FMEA-Workshop_2026-03-12_Notes.docx` mentions an assembly in passing and must not yield `design_item`
from prose. The cropped worksheet screenshot lost its anchoring header block to the crop — the one part
carrying the item — and its EXIF absence proves nothing. `RE_ DFMEA action 14 - severity downgrade.eml`
carries a *claim about* a ranking without the analysis, and a ranking is never a fact of the item anyway.
All three may sit in an accepted analysis neighbourhood; none receives a label from it.

## Audits run

`python3 -m json.tool` parses. All 13 `file_examples.source_type` and all 9 `file_kinds.source_types` are
in `SOURCE_TYPES`. All 10 `collides_with.domain` resolve to roster `domain_id`s; both `also_holds_with`
targets resolve to roster **schema** ids and are already declared on the anchor's own schema-level
`also_holds_with`; every `also_schema` resolves to a schema id. All 4 `falls_through_to` names are §7.3
residuals and cover every per-file `falls_through_if_inactive` (empty difference). Fifteen quoted spans
were checked verbatim against `00`: **14 matched**. The fifteenth — *"calculated margins or performance
against named requirements"* — is quoted from `engineering.json`, not `00`, and the JSON now says so
inline. A naive alternating-backtick extractor reports twenty further "misses"; those are the connective
prose *between* quoted spans and were read by hand. **No `00` quotation here is fabricated or paraphrased
inside quote marks.** No threshold, score, evidence count or handling class appears. `fields`,
`proposed_fields`, `dimension_order` and `role_split` are each empty *with a note saying why*. Only the two
assigned files were written; `29-DOMAIN-OWNERSHIP.md`, the roster, `canonical_fields.json`,
`engineering.json` and every neighbour node are untouched.

## Recommendations to R1c (not made here)

1. `business_operations.risk-register`'s one-way edge is now reciprocated from this side using its own
   discriminator and the same two fixtures. That file was not edited.
2. NJ-BOM-1 names this row as a co-defendant. The defence is the clause-and-fixture asymmetry table above,
   which is mechanically re-checkable. Apply the same test en bloc to `cad-model`, `drawing-package`,
   `electrical-schematic`, `change-order`, `material-specification`, `prototype-build`,
   `verification-validation` and `simulation-analysis` — several of those (change-order,
   verification-validation, simulation-analysis) map onto default clauses and are likely refusals on this
   test, while `pcb-layout` and this row are not.
3. If NJ-FMEA-2 resolves toward omitting `design_item` for process-object analyses, a grouping_reason on
   `engineering.json` carries the coverage — one process step's prospective analyses and the controls they
   generate. Recommended, not written.

## NEEDS-JOSEPH (this node only)

- **NJ-FMEA-1 — the value-named engineering rows must be decided en bloc.** This id is a verbatim member
  of the anchor's `work_types[]`; `bill-of-materials` refused on that ground and `pcb-layout` survived it.
  This row argues it belongs with `pcb-layout` on the clause-and-fixture asymmetry, but the outcome must
  not depend on which agent drew which id. **(a)** keep the value-named rows whose structures are absent
  from the default and refuse the rest — what this argument implies; **(b)** demote them all to browse-only
  values feeding the artifact-type field, a P6 values table not a roster — cheapest, and loses the four
  structures and ten reciprocal boundaries researched here; **(c)** require each to be redefined as a
  situation, which is what this row did and which no row can do for its siblings.
- **NJ-FMEA-2 — a process FMEA and a HAZOP analyse an object no proposed key can hold.** Their row objects
  are process steps and plant nodes; `design_item` denotes a designed configuration item. Widen
  `design_item` to any analysed object (one key, two meanings — `PFMEA_Line-3_Bushing-Press_Rev4.xlsx` and
  a brake assembly become indistinguishable at the same level); omit the level for process objects (what
  the row recommends today, leaving half this material one level shallower than the other half); or mint
  an analysed-object key on the shared vocabulary, which one template row must not do. **Recorded, not
  resolved. No field was proposed.**
- **NJ-FMEA-3 — which residual owns a plant hazard study, and does the answer change prompt policy?**
  `Review Later` is recommended and encoded. But a process hazard study enumerates how to cause a release,
  and if Joseph accepts that security-relevance argument the correct residual is `Protected Records` —
  which changes not just a name but whether this material may reach a model at all, since `00` requires
  such material *"must not cause filenames or content to be exposed in model prompts"*. That is a product
  decision about a whole class of engineering files, so it is surfaced rather than chosen.
