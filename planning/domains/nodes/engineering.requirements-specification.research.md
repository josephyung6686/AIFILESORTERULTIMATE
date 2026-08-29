# engineering.requirements-specification — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.requirements-specification.json`](engineering.requirements-specification.json).
**Verdict: `refuse_node: true`.** No salvage — both files are new in this pass.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — the standing brief, read in full. Its six
  requirements are what this memo is audited against, and its instruction that a refusal is a
  success is what made it possible to write this one honestly.
- `python3 planning/domains/dispatch/make_prompt.py engineering.requirements-specification` — the
  stamped assignment. It supplied the row metadata, the node test, the output shape, and the
  `must_consider_neighbors` list (`manufacturing`, `code`, `research`) and
  `must_consider_residuals` list (`Independent Records`, `Review Later`).
- `planning/domains/nodes/engineering.json` — **the decisive source.** The schema anchor is written
  at J-DEPTH and its default template is what this row is measured against. I read its
  `recognition`, `node_test`, `proposed_fields`, `work_types`, `template`, `collides_with`,
  `falls_through_to`, `sensitivity_why`, `open_question` and its twelve `file_examples` filenames.
- `planning/domains/CONNECTION.md` §2, lines 90–97 — the node test itself, read directly rather
  than through the prompt's paraphrase.
- `planning/00-database-agent-product-design.md` — reached by `grep -n` for the two residual
  sentences only. Both quotations in the JSON were matched verbatim against line 120 before being
  written. Nothing else in this row quotes `00`.
- `planning/domains/roster.json` — every edge endpoint checked mechanically. All five
  `collides_with` domains resolve to roster `domain_id`s; both `falls_through_to` names are §7.3
  residual names.
- `src/evidence_shape/vocabulary.py` — via the fourteen-member `SOURCE_TYPES` list, checked
  against all eight file examples and the `file_kinds.source_types` list.
- One landed launch row for calibration: `finance.crypto-assets.research.md`.
- Neighbour boundaries, found with one grep for this id under `planning/domains/nodes/`:
  `business_operations.product-requirements.json` and `.research.md`,
  `engineering.material-specification.json` and `.research.md`,
  `engineering.automotive-program.json` and `.research.md`,
  `engineering.change-order.research.md`, `engineering.invention-disclosure.research.md`.
  Four of those files already argue a boundary against this id; all four are reciprocated below.

I did not read any other row, and I edited nothing outside my two files.

---

## THE CHARGE — the strongest case that this row should not exist

I make the case at full strength first, because it is the case that won.

**This row is its own schema's default template, and the schema row proves it in its own text.**

The engineering schema row's `recognition.deterministic` list contains, as its second entry:

> a requirements structure whose rows carry stable requirement identifiers and whose columns or
> linked records name allocation, rationale, verification method and verification status for an
> identified system or item

That is not adjacent to what this row would detect. It *is* what this row would detect, in the
schema author's own words. And the schema row's twelve default `file_examples` open with
`SYS-REQ-042_Braking-System-Requirements_RevB.docx` — a system requirements specification is the
**first** fixture the engineering schema uses to illustrate itself.

The precedent is already on the roster. `engineering.automotive-program` was refused with the
reasoning that "a template whose fixtures are the schema's own default fixtures is the schema's
default template." That row's fixtures were the schema default's fixtures *collectively*. This
row's core fixture is the schema default's *first* fixture, singly and exactly.

**Second charge — this row is a value.** The schema row's `work_types` list already contains
`stakeholder or system requirement` and `requirements traceability matrix`. Its proposed
`engineering_artifact_type` field is an enum whose stated role spans "requirement, drawing, CAD
model, schematic, calculation, interface definition, change request and verification record."
This id is two entries of that enum given a node. The brief and ALIGNMENT both name that move:
work types are values, and minting a node for a dropdown option is the 574's original mistake.

**Third charge — this row is a document type.** The assignment's own `one_line_hint` is a
document-type definition: "A document that states what a product, system or component must do, and
how conformance will be shown." A membership test of the form *the document is called a
specification* is a document-type word wearing a node's clothes, and document-type words are
constitutionally never-alone evidence.

**Fourth charge — the residue is a lexical trap.** Subtract the schema default and the sibling
rows and what remains is the word *requirements*, which is the single most promiscuous token in
this material: `requirements.txt` is a Python dependency manifest, *Job Requirements* is a
recruitment document, *Visa requirements* is an immigration checklist. A row whose remaining
distinctive content is a homograph is not a row.

---

## Attempting to defeat the charge — three legs, each argued separately

CONNECTION.md §2 line 94: "A **template** row exists only if its detection signals, recommended
dimensions, or privacy rules differ from its schema's default template." I worked each leg
independently and looked for the strongest available defence of each.

### Leg 1 — detection signals. **SAME.**

There is no defence to construct. The schema's deterministic signal 2 is quoted above. The
strongest thing I could add would be a requirement-identifier *namespace* signal (SYS-REQ-, IFC-,
SRD-), but an identifier pattern is R2's territory, the schema already names "stable requirement
identifiers" as part of its own signal, and a bare identifier is on the schema's own `never_alone`
list ("a part number, drawing number or other short identifier alone"). Writing a second detector
for one structure would give the same bytes two claimants on the same schema — a worse outcome than
having no row.

### Leg 2 — recommended dimensions. **SAME, level for level.**

The default is `project → design_item → lifecycle_stage → engineering_artifact_type` with
`revision_or_baseline` held as metadata. Three sibling rows survived by departing from it, so I
tried each departure here.

**(a) The `engineering.material-specification` inversion — drop `design_item`, anchor on the
document.** That row survived because a material specification "is invoked by many design items and
outliving all of them" and "the schema default cannot activate here because there is no design item
in the file." The move does not transfer. A requirements specification is *allocated to* the item it
defines; at system level its identity **is** the item's identity. `SYS-REQ-042` is the braking
system's definition, not a reusable instrument the braking system happens to cite. There is nothing
to hoist above `design_item` because the document is not separable from it.

**(b) Scope the row to requirements that have no design item yet** — the stakeholder-needs case.
This is the most tempting defence and the one I spent longest on. It fails twice. First, the
schema's own signal requires the structure to be "for an identified system or item", so a
requirements document with no item **does not activate the engineering schema at all**; it falls
through to `Review Later`, and a template cannot be built on ground its schema never reaches.
Second, and fatally, the row would then be defined by the *absence* of the default's second
dimension — which the brief names explicitly as a disqualifier ("a row defined only by the ABSENCE
of something"). Fixture: `Stakeholder-Needs_Workshop-Notes_2026-03-11.docx`, kept in the JSON
precisely to record this dead end.

**(c) The `engineering.change-order` departure — drop `lifecycle_stage`.** That row's memo argues a
gate review "is *about* lifecycle stage, which is precisely the dimension this row drops." Here the
sign is reversed. A requirements document is the artifact that carries lifecycle state most
explicitly of all — draft, reviewed, baselined at a named design review, released. The level is
*more* load-bearing than in the default, not less. There is no drop available.

**(d) A requirement-level axis: system → subsystem → component.** Real in the world, and not a
folder dimension. It is the allocation relation, which the schema's own signal already names as a
*column inside the artifact*. That is a trace graph. `00`'s discipline that facts are not paths
applies directly: an allocation link is a fact about two requirements, not a level.

### Leg 3 — privacy rules. **SAME, with the same stated reason.**

The schema row is `potentially_sensitive` because engineering packages carry "proprietary design
definition, supplier data, vulnerabilities, safety analyses, export-controlled or critical-technology
information, signatures and test evidence." A requirements specification is the centre of that
sentence, not an exception to it — safety allocations and export-controlled performance figures live
in requirements before they live anywhere else. Leg 3 asks whether the rules *differ*. They do not
differ; they coincide exactly.

**Zero legs. Refuse.** Nothing was invented to keep the id: `fields: []`, `proposed_fields: []`,
`work_types: []`, `dimension_order: []`, no context terms, no new key.

### Where the survival case remains real, and why it does not win

It is not dismissed. Requirements are probably the highest-volume document class in a real
engineering corpus, and a user browsing a tree would very likely expect a folder with this name.
But volume is not the node test and neither is browse expectation: `parent_id` is browse-only, and
the test is about which evidence activates. On evidence this row and the schema default are the
same object. If the id survives at all it survives as a browse label under `engineering`, which is
R1c's call and is raised as NJ-REQ-1.

---

## The collision fixture

**`requirements.txt`.** It is `code_structured`, it sits at a repository root, its filename contains
this row's defining word, and it contains not one shall-statement, not one requirement identifier,
no verification method and no design item. **What discriminates it: the absence of every structural
element and the presence of only the word.** It is in `collides_with → code` rather than merely in
the rejected list because it is the file most likely to be mis-routed by any future revival of this
id — the resemblance is one hundred percent lexical and zero percent structural, which is exactly
the condition `00` warns about when it forbids inferring meaning from a name.

A second, blunter one is kept as a file example: `Job Requirements - Senior Mechanical Engineer.pdf`
puts *requirements* and *engineer* in one filename and is a recruitment document. Together the two
establish the `never_alone` rule that neither the word nor the word-pair can ever be a signal.

---

## Files considered and rejected

The tempting false positives, and why each is not this row's evidence:

- **`SYS-REQ-042_Braking-System-Requirements_RevB.docx`** — the paradigm case, and the one that
  kills the row rather than making it. It is the engineering schema row's own first file example.
  Claiming it would be claiming the schema's default fixture.
- **`RTM_Braking-System_RevB.xlsx`** — a requirements traceability matrix. The hardest rejection,
  because its structure (requirement id × method × status × evidence pointer) really is distinct
  from a drawing's. But `requirements traceability matrix` is a literal entry in the schema row's
  `work_types` list, and its detection is the second half of the schema's signal 2 ("columns or
  linked records name allocation, rationale, verification method and verification status"). A value.
- **`Requirements specification - Rev C.pdf`** — `business_operations.product-requirements` holds
  this as its second collision fixture and cedes it *to this id*. It goes to the engineering schema
  default instead. The discriminator that row names — the verification-method column plus standards
  references — is untouched by this refusal; only the destination's name changes.
- **`CTS_Brake-Pedal-Assembly_OEM-XJ_Rev4.pdf`** — the refused `engineering.automotive-program`
  ceded these bytes to this id. A customer technical specification differs from an internal one only
  by its **issuer**, and an issuer is an organisation name: `00`'s university-name defect exactly.
- **`Product Specification.docx`** — `engineering.material-specification` names this shared fixture
  from its side, with the invocation-is-a-link rule. Its functional half is the schema default's
  ground.
- **`ISO 26262-6_2018.pdf`** — a received published standard: numbered clauses, shall-statements,
  verification provisions, an issue year. `engineering.standards-library` owns it on issuer role.
  Notable that the *same* issuer-role discriminator resolves this id away twice (here and against
  material-specification) — a sign the id is a document-type word rather than a situation.
- **`ECR-1187_BPA-210_Bushing-Material.pdf`** — an engineering change request. Rejected as an edge,
  not just as a fixture; see below.
- **`BPA-210_DVT-07_Verification-Report.pdf`** — the "how conformance will be shown" half of the
  hint. It is `engineering.verification-validation`'s, and also the schema default's sixth fixture.
- **`Sprint-14-Project-Status.xlsx`** — the schema row's own `business_operations` collision
  fixture. An engineering team and a project name are not an engineering schema.
- **`Visa requirements checklist.pdf`** — the word in a wholly different world; `Independent
  Records`. Not kept as a file example because it teaches nothing beyond the lexical rule the two
  kept traps already carry.
- **A `.reqif` export from a requirements-management tool** — genuinely structured, genuinely
  requirements. Rejected as a fixture because an extension is never sufficient alone (`00`) and
  because it is the schema default's signal 2 in a machine-readable wrapper. It stays in
  `file_kinds.extensions` as a routing hint only.

---

## Reciprocal boundaries — both directions, same fixture on both sides

Written so a neighbour's author can lift them verbatim. Full text is in the JSON.

| Neighbour | Seam | Shared fixture, named on both sides |
|---|---|---|
| `business_operations.product-requirements` | verification-method column + standards references vs user stories, acceptance criteria, non-goals | `Requirements specification - Rev C.pdf` → the engineering **schema default** (that row already cedes it) |
| `engineering.material-specification` | the specified object: a system's behaviour vs a substance, component or process | one `Product Specification.docx`; the MS-4120 invocation links, it does not relocate |
| `engineering.verification-validation` | which artifact carries the measured outcome — the matrix carries a pointer, the report carries the evidence | `RTM_Braking-System_RevB.xlsx` vs `BPA-210_DVT-07_Verification-Report.pdf` |
| `engineering.standards-library` | issuer role: standards body or regulator vs the holder's own engineering function | an `ISO 26262` part → standards-library |
| `code` | structure vs word: repository dependency manifest vs a controlled clause document | `requirements.txt` → code, on both sides |

The two boundaries already written **against** this id by landed rows are reciprocated in matching
terms and neither is contradicted: `business_operations.product-requirements` keeps the
verification-method discriminator, `engineering.material-specification` keeps the specified-object
discriminator. Both continue to work after the refusal; the only change is that the winning side
resolves to `engineering` rather than to this id. That is a recommendation to R1c, recorded in
NJ-REQ-1 — **I did not edit either neighbour file.**

## Neighbours considered that did **not** get an edge

- **`engineering.change-order`** — its memo already rejected an edge to this id, reasoning that "a
  requirements document has requirement rows and verification methods, not a from/to revision pair
  on an item." I agree from this side and reciprocate the rejection rather than manufacture a mutex.
- **`manufacturing`** (an assigned must-consider) — a specification is cited by inspection plans and
  first-article reports, but the discriminating evidence never competes: manufacturing keys on
  batch, asset, operation and nonconformance. The schema row already carries this collision at
  schema level, and duplicating it on a refused template would be noise.
- **`research`** (an assigned must-consider) — a research protocol has objectives, not shall-clauses
  allocated to an item. The schema row already holds this seam with the FEA-versus-paper fixture.
- **`engineering.stage-gate-review`** — close, and rejected on leg 2's own logic: a gate review is
  about the lifecycle level, which this row cannot drop.
- **`legal.*`** — a contract has numbered clauses and a shall vocabulary, and a statement of work
  can read as a specification. Rejected because the discriminating structure is the executed-
  instrument form (parties, signatures, consideration), which no requirements document has, and
  because no fixture actually sits between them.
- **`role_split`** — empty, and the refusal is worth stating: the split this material wants is the
  *issuing* party against the *responding* party on a customer specification, both in labelled slots
  on one cover page. No canonical key exists for either role, and minting one to serve a refused row
  would be indefensible.
- **`also_holds_with`** — empty by contract (`_CONTRACT.md` restricts it to schema rows) and empty
  on the merits.

## Fields

`fields: []` and `proposed_fields: []`. PR-6 leaves the engineering schema fieldless, a template may
reuse only what its schema declares, and a refused template proposes nothing. The four keys this
material would want — `design_item`, `lifecycle_stage`, `engineering_artifact_type`,
`revision_or_baseline` — are already the schema row's proposals awaiting R1c; reproposing them here
would create the duplicate-spelling problem that row explicitly warns against. No context terms are
proposed either: `00` states the pattern-plus-context shape for course codes only, and a refused row
should not seed a detector.

## Audits run before returning

- `python3 -m json.tool` — parses.
- Both `00` quotations matched verbatim by `grep -n` against `planning/00-database-agent-product-design.md`
  line 120 **before** being written. No other `00` quotation appears in either file. Nothing is
  paraphrased inside quote marks.
- The CONNECTION.md §2 sentence and the engineering schema row's deterministic signal 2 were both
  read from source and quoted verbatim in this memo; neither is attributed to `00`.
- All 8 `file_examples.source_type` values and all 6 `file_kinds.source_types` values are in the
  fourteen-member `SOURCE_TYPES` list.
- All 5 `collides_with.domain` values resolve to roster `domain_id`s; both `falls_through_to` names
  are §7.3 residuals; `also_holds_with` and `role_split` are empty with notes.
- No threshold, score, count or handling class appears. `sensitivity` is `potentially_sensitive`.
- No file example writes a folder path as a fact; the one sparse fixture carries
  `group_without_copying_facts: true`.
- Only the two assigned files were written. `29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `check.py`, `src/`, the SPECs and every neighbour node are untouched.

## NEEDS-JOSEPH (this node only)

- **NJ-REQ-1 — does the refused id survive as a browse-only label, or is it dropped?** Three
  neighbour files name this id in their own text: `business_operations.product-requirements`
  (collision + fixture), `engineering.material-specification` (collision + `needs_llm` +
  `one_line`), `engineering.automotive-program` (collision, itself refused). Option (a): keep the id
  with `refuse_node: true` as a browse shelf under `engineering`, and the three neighbours read
  correctly as written. Option (b): drop it from the roster, and those three files carry a dangling
  target that must be repointed at `engineering`. I recommend (a) and did **not** edit any neighbour.
- **NJ-REQ-2 — is `engineering.verification-validation` also the schema default?** I did not test it
  and must not. But the schema's signal 7 is a verification matrix, and its sixth default fixture is
  a verification report — the same relationship this refusal found on the requirements half. If both
  halves of the hint's sentence are the schema default, the honest conclusion is that the
  `engineering` schema takes template rows only for its *inversions* (`material-specification`,
  `change-order`, `standards-library`) and not for its paradigm artifacts. That is a shape decision
  about the whole schema, not one row's call.
- **NJ-REQ-3 — the re-examination trigger.** If R1c adjudicates `revision_or_baseline` as
  destination-eligible, or licenses a released-baseline template, a requirements corpus would file
  by baseline rather than by item and leg 2 would genuinely differ. That would be a real dimensional
  difference rather than the absence-based one rejected here, and this refusal should be reopened.
  Stated as a trigger rather than left as an unrecorded hedge.
