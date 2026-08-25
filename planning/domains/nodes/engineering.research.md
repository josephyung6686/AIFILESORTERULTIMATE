# engineering — full-depth research memo

J-DEPTH: FULL R1b DEPTH (schema default researched before any child templates).
Status: **PASS, conditional on R1c field adjudication; not an industry-label schema.**
Row: `engineering` (`kind: schema`, `launch: placeholder`).
Outputs owned: `planning/domains/nodes/engineering.json` and this memo only.
JSON was authored first; this memo records and checks the same verdict.
PR-6 is obeyed: `fields: []`; all non-canonical candidates are proposals, not legal facts.
Default researched order, conditional on field approval: project → design item → lifecycle stage → engineering artifact type.

## Verdict in one sentence

Keep `engineering`, but define it narrowly as the controlled technical definition and evidence chain
of an identified physical or system design item. Refuse the broad reading “files from an engineering
company.” An engineering department's project schedule is business operations; a production
traveler is manufacturing; a contract drawing for one site is construction/property; a repository
is code; and an exploratory experiment whose product is knowledge is research. The row passes only
because configuration identity plus traceable requirements/change/verification produces a
structural field set and activation apparatus those neighbours do not have.

## Sources and authority stack

Local binding sources read: `planning/00-database-agent-product-design.md`, its numbered rendering
`planning/01-product-design-structured.md`, `planning/prompts/ALIGNMENT.md`,
`planning/domains/CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `_CONTRACT.md`,
`canonical_fields.json`, `roster.json`, `ROSTER.md` §4 and Appendix A, and
`src/evidence_shape/vocabulary.py`. Adjacent landed rows were read, not edited:
`construction_property.json`, `business_operations.json`, its exemplary refusal
`business_operations.organisational-records.json`, `research.json`, `academic.json`, and available
child rosters. `manufacturing.json` had not landed when research began, so its dispatched hint and
roster children were used; no absent content was guessed as if reciprocal.

Primary external references used as domain evidence, not as quotations attributed to `00`:

- NASA, *Systems Engineering Handbook*, NASA/SP-2016-6105 Rev 2, especially technical data
  management, interface management, configuration management, verification and validation. It
  defines a technical data package around an **item** and its required design configuration and
  names drawings, associated lists, specifications, standards, performance requirements, quality
  provisions and packaging details as possible members.
- NASA Systems Engineering Handbook's interface-management guidance names interface requirements
  and interface control documents/drawings, approved interface changes, product verification and
  validation, configuration management and the project technical data package as one trace chain.
- FAA Order 8130.34 Appendix C asks how drawings, test procedures and engineering changes are
  controlled and separately asks about software lifecycle data. That separation supports, but does
  not by itself dictate, the code seam.

Only `00` is quoted as design authority in JSON. External descriptions are paraphrased or clearly
attributed; they do not become fabricated design quotations.

## Bottom-up file study

The JSON carries twelve full fixtures. The following notes make the observation/fact split and the
rejections explicit.

1. **`SYS-REQ-042_Braking-System-Requirements_RevB.docx`** (`text_document`). Inside are a labelled
   document-control block and stable requirement rows with allocation and verification-method
   columns. The filename's `RevB` is only an observation; the labelled revision cell is stronger.
   If the schema eventually has fields, the item, lifecycle stage and engineering artifact type
   become eligible. Today only universal facts are legal. Rejected inference: a folder path, or a
   released baseline from the suffix. Inactive residual: Independent Records.
2. **`BPA-210-001_Brake-Pedal-Assembly_RevC.dwg`** (`design_creative`). A title block relates an
   assembly, drawing identifier, scale, revision, issue status and approval. That *relation*, not
   `.dwg`, is the signal. The exact same bytes would be construction/property if the title block
   instead made this a contract sheet about a named site and instruction. Inactive and unreadable:
   Unsupported or Encrypted.
3. **`BPA-210_Product-Structure.xlsx`** (`spreadsheet`). Parent assembly, child identifiers,
   quantities, drawing revisions, release and approver make a design-authoritative product
   structure plausible. A spreadsheet headed BOM without those roles could be a production pick
   list, procurement list or cost sheet. That collision is not smoothed away. Residual: Review Later.
4. **`ECR-1187_BPA-210_Bushing-Material.pdf`** (`text_document`). Affected item, current/proposed
   revision, technical reason/effect and approval state make a controlled engineering change. A
   schedule/scope change with owner and due date is business operations. A shop-floor deviation can
   additionally activate manufacturing; the cause does not erase the approved design change.
5. **`BPA-210_FEA_Loadcase-3_RevA.pdf`** (`text_document`). Model/configuration inputs and a result
   traced to requirement `SYS-REQ-042` make analysis part of a controlled design evidence chain.
   Simulation vocabulary alone does not distinguish research. A comparative study without an
   affected item belongs to research.
6. **`BPA-210_DVT-07_Verification-Report.pdf`** (`text_document`). Configuration-under-test,
   deviations, requirement-to-procedure links and result disposition are stronger than a generic
   pass/fail table. The latter is manufacturing inspection just as often. A production-
   representative article can legitimately hold both schemas.
7. **`PDR_Braking-System_2026-04-18.pptx`** (`presentation`). Requirements allocation, interfaces,
   risks and open technical decisions support engineering; schedule/status slides support business
   operations. This is `also_holds_with`, not a winner-takes-all category decision.
8. **`TDP_BPA-210_Baseline-C.zip`** (`archive`). The manifest names a coherent requirement,
   drawing, associated-list, specification and verification set for one item/baseline. The normal
   scan does not extract members to disk. No uninspected member content becomes a fact.
9. **`margin_plot.png`** (`image`). This is the sparse-file test. Axes and legend do not identify an
   item or requirement; absent EXIF does not prove screenshot. It may join an accepted analysis
   neighbourhood, but `design_item = BPA-210` is not copied from neighbours. Residual: One-Off Images.
10. **`Sprint-14-Project-Status.xlsx`** (`spreadsheet`) — collision fixture, rejected. Owner, due
    date, completion and traffic lights are project-delivery evidence. The engineering department
    name is never-alone. Same bytes must be described on both sides: business operations accepts it;
    engineering rejects it because there is no controlled design item or technical-definition trace.
11. **`LOT-24-081_Final-Inspection.xlsx`** (`spreadsheet`) — collision fixture, rejected. Batch,
    station, measured values and inspector disposition are manufacturing execution. A cited drawing
    revision is governing evidence, not proof that the record defines the design.
12. **`A101_Ground-Floor-Plan_Rev4_IFC.pdf`** (`text_document`) — collision fixture, rejected from
    engineering as default. Site, contract sheet number and issued-for-construction status make it
    construction/property. Infrastructure/plant packages remain NJ-ENG-3 because they can state
    both a configured system item and a site instruction.

Ugly routes covered: labelled forms versus free prose; image/OCR ambiguity; archive manifests;
presentations; spreadsheets; unsupported CAD; mixed schemas. Email and calendar are plausible
source types but intentionally absent as activation fixtures: a design-review invitation or change-
board email is correspondence around a controlled artifact, not proof of the schema until it cites
the affected item and controlled record. Their contents can join a group; source type never fires.

## The node test, all three legs

### Leg 1 — distinct field set

The default requires four destination concepts and one metadata concept:

- canonical `project`, if R1c permits this placeholder schema to reference it;
- proposed `design_item`, the controlled physical/system item the evidence defines;
- proposed `lifecycle_stage`, unless canonical research `stage` is widened;
- proposed `engineering_artifact_type`, unless canonical `artifact_type` is widened;
- proposed non-destination `revision_or_baseline`, distinct from universal `version_family`.

`design_item` is load-bearing. Project does not substitute: a project has many systems, assemblies
and interfaces; an item can persist across projects and modifications. Construction/property's
proposed property is a site/premises, not the thing defined. Manufacturing's roster hint keys on a
batch, asset or nonconformance: those are realized/execution objects, not the intended definition.

The two near-duplicate proposals are candid, not hidden. Canonical `stage` is currently “where in
its workflow a research artifact sits”; canonical `artifact_type` is shared by research and code.
R1c may widen both. If it does, the engineering spellings must disappear rather than coexist as
synonyms. The JSON records that exact adjudication.

`revision_or_baseline` is not `version_family`. A family says several files are variants of one
logical document. A labelled revision says which controlled issue one file represents; a baseline
is a set of controlled items and may contain different revisions. It remains metadata because a
revision-first folder design fragments the item and risks obsolete issue labels.

**Leg 1 verdict: passes conditionally.** If Joseph rejects `design_item` and also forbids widening
the canonical research/code keys, this schema must be refused rather than reduced to `project` plus
industry words.

### Leg 2 — detection signals

The strongest signal is a relation, never a token: identified item + controlled technical
artifact + revision/status/trace structure. Concrete shapes are title blocks; requirement rows with
allocation and verification columns; item-centered technical data package manifests; engineering
changes with affected and replacement configurations; product structures; analyses tied to named
requirements; and verification matrices naming the configuration under test.

These are not generic “engineering file extensions.” They survive the deletion test: delete the
company name, the word engineering and the extension, and the labelled roles still express which
item, which controlled definition and which evidence link the record carries. Delete the item/
configuration relation, and the schema no longer fires.

**Leg 2 verdict: passes.** Revision control helps distinguish the row from a loose project folder,
but cannot distinguish it from code or construction by itself; the JSON therefore places revision
alone in `never_alone`.

### Leg 3 — privacy rules

The row is potentially sensitive for a domain-specific reason: controlled technical packages can
contain proprietary product definition, supplier restrictions, safety margins, vulnerabilities,
critical-technology/export restrictions and signatures. NASA's technical-data guidance explicitly
discusses distribution statements and protection of critical-technology, IP and proprietary data.
That is stronger than “all documents might be sensitive,” but it does not justify inventing a
handling class or making engineering a safety domain. `00`'s privacy-before-model rule remains the
operative product rule.

**Leg 3 verdict: passes as a different default risk profile**, though field/detection distinctions
already carry the node without relying on privacy alone.

## Default template and why children come later

PR-6 requires the JSON's actual `dimension_order` to be empty because this placeholder schema
declares no legal fields. The researched default, pending R1c, is:

`project → design_item → lifecycle_stage → engineering_artifact_type`

Project precedes time because `00` says project/function/subject usually comes before time in
document domains. Design item makes “detailed design,” “verification” and “drawing” intelligible.
Revision is deliberately not a level. The user may flatten or reverse later; this is a recommendation,
not a path fact.

This default was researched before roster children. Child names such as requirements specification,
CAD model, drawing package, simulation, change order, prototype build and verification/validation
are mostly artifact/lifecycle values. They survive as templates only if their detection signals,
dimensions or privacy truly differ from this default. This memo does not pre-approve them.

## Reciprocal neighbour boundaries

### Manufacturing ↔ engineering

Engineering accepts a record when it defines, changes or verifies the intended configuration.
Manufacturing accepts it when it records making, inspecting, maintaining or correcting a realized
unit/batch/asset. `LOT-24-081_Final-Inspection.xlsx` is manufacturing even though it cites an
engineering drawing revision. In the other direction, `ECR-1187` remains engineering when it
approves a material change even if a nonconformance triggered it. One file may hold both when both
structures are explicit. Reciprocal authoring remains R1c because manufacturing had not landed.

### Code ↔ engineering

Repository root/package/source structure belongs to code. Item/baseline/product-structure evidence
belongs to engineering. Revision, requirements and tests are shared and never sufficient. Embedded
firmware can carry both: repository facts do not disappear when firmware becomes a configured
component, and item/baseline facts cannot be inferred from the repository's employer or README.

### Research ↔ engineering

Research is knowledge-centered: project, stage, artifact, lab, venue. Engineering is design-item-
centered: requirement, controlled definition, change and realization evidence. The exact FEA PDF
is engineering when it identifies BPA-210 and SYS-REQ-042; remove those relations and make it a
comparative methodology study and research accepts it. An R&D prototype can carry both.

### Business operations ↔ engineering

Business operations owns delivery/governance: schedule, budget, owner, status, portfolio and generic
change. Engineering owns technical definition. `Sprint-14-Project-Status.xlsx` is the shared fixture
bytes: business operations accepts; engineering rejects. A formal design-review deck may carry both
when it contains technical baselines and governed project decisions.

### Construction/property ↔ engineering

Construction/property's landed default is property/site joined to professional instruction and
contract lifecycle. Engineering is configured item joined to controlled definition. The A101 sheet
is construction/property because it is site/contract information. A reusable equipment-assembly
drawing is engineering. Plant and infrastructure can state both; NJ-ENG-3 asks whether both should
normally activate or whether the primary-object relation should choose.

## Files considered and rejected

- Generic Gantt chart, project status report, action log and budget: business operations, because
  none defines a controlled item.
- Production traveler, lot history, final inspection, calibration certificate, maintenance work
  order and CAPA: manufacturing unless they separately approve a design-definition change.
- Site diary, issued-for-construction site sheet, variation claim and as-built property handover:
  construction/property unless a configured system relation independently exists.
- Git repository, package manifest and CI test report: code unless the release is explicitly tied
  to a physical/system configuration baseline.
- Downloaded standards PDF and vendor component datasheet: reading/reference or engineering
  standards/material-specification template only with accepted project/item evidence; names alone
  do not activate the schema.
- Academic CAD assignment: academic on course/term evidence. A drawing format and revision table do
  not convert coursework into a professional controlled design definition.
- Research simulation, notebook and prototype: research when the object is investigation rather
  than an identified product/system configuration.
- Patent or invention disclosure: may be engineering's invention-disclosure template and legal IP
  protection, but the schema default cannot infer controlled design fields from “invention.”

## Proposed fields and exact adjudication

1. `design_item` — genuinely new role; recommended accept. No canonical key identifies the item
   whose design configuration the package defines.
2. `lifecycle_stage` — accept only if canonical `stage` stays research-specific; otherwise widen
   `stage` and drop this proposal.
3. `engineering_artifact_type` — accept only if canonical `artifact_type` stays research/code-
   specific; otherwise widen `artifact_type` and drop this proposal.
4. `revision_or_baseline` — metadata/search only; decide whether labelled controlled revision is a
   fact distinct from universal `version_family` or remains observation/version-graph state.

No organization, author, client, part number, discipline, standard, material or date key was minted.
They are either roles already represented elsewhere, search evidence, values, or tempting expansion
that would turn a small schema into an engineering PLM database.

## Neighbours considered without an edge

- `academic`: the CAD-course collision is real at file level, but academic activation depends on
  school/term/subject/work-type evidence and does not compete on the controlled-definition fixture
  once course context is present. The boundary is adequately carried by never-alone evidence; an
  extra edge would imply ordinary professional ambiguity where the roster did not require it.
- `legal`: executed licences, patents and regulated approval instruments can coexist with technical
  evidence, but they activate legal on execution/rights/protected-record structure, not on the same
  technical-definition observations. The invention-disclosure child should research this edge.
- `creative`: industrial-design renderings and CAD previews can be creative assets, but visual style
  alone neither proves nor conflicts with configuration control. The industrial-design child owns
  the narrower seam.
- `government`: regulatory submissions and approvals may contain engineering packages, but authority
  role versus applicant-held technical definition is disjoint evidence. Certification/airworthiness
  children should research it rather than broadening the schema default.

## NEEDS-JOSEPH

- **NJ-ENG-1:** Widen canonical `stage` and `artifact_type` to cross-domain roles, or preserve
  `lifecycle_stage` and `engineering_artifact_type`? Alternatives are explicit; shipping both
  spellings for one role is rejected.
- **NJ-ENG-2:** Is labelled controlled revision/baseline a domain fact distinct from universal
  `version_family`, or only observation plus version-graph metadata? The memo recommends a non-
  destination fact if accepted.
- **NJ-ENG-3:** For infrastructure and plant packages, does explicit configured-system evidence
  normally activate engineering alongside construction/property, or does site-bound instruction
  make construction/property primary unless reusable product evidence exists?
- **NJ-ENG-4:** Product discovery, customer requirements and roadmaps with no controlled design item
  remain business operations/research under this row. Confirm that engineering begins only when a
  controlled technical definition emerges.

## Consistency and completion check

- JSON first, then memo: yes.
- First eight lines include J-DEPTH, verdict, row, ownership, JSON-first, PR-6 and researched default.
- Universal keys appear in every fixture's legal-fact list as applicable; no proposed field is
  written as legal before adjudication.
- At least eight concrete files: twelve, including labelled documents, sparse image, archive,
  collisions and multi-schema cases.
- SOURCE_TYPES are closed-vocabulary values from `vocabulary.py`.
- Work types are values, not children.
- Folder paths are never facts.
- Sparse grouping does not copy item/project facts.
- Edges use roster ids; residuals use `00`'s exact names.
- Exact `00` quotes in JSON are confined to residual design cites and were checked against `00`.
- No threshold, confidence score, detector regex, handling class, field row or neighbour edit was
  authored.
- JSON and memo agree: **keep the schema conditionally**, proposed fields are exactly
  `design_item`, `lifecycle_stage`, `engineering_artifact_type`, `revision_or_baseline`; open items
  are exactly NJ-ENG-1 through NJ-ENG-4.

**Complete ending:** engineering is a real schema only as the controlled definition of an identified
designed item. If R1c cannot license that structural fact set, refuse the row rather than falling
back to the engineering-industry label.
