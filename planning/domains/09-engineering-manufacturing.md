# Domain catalogue — engineering, manufacturing and the physical trades of industry

Supercategory: `engineering-manufacturing` · Authored: 2026-08-21 · Entries: **45**

Conforms to [`_CONTRACT.md`](_CONTRACT.md). Machine-readable form: [`09-engineering-manufacturing.json`](09-engineering-manufacturing.json) — the JSON is the artifact the §3.6 validator consumes; this file is the same content as tables.

Provenance: **design 0 · inference 3 · proposal 42**. Sensitivity: **potentially_sensitive 7 · none 38**.

Every quotation in this file was pulled from `00-database-agent-product-design.md` by the generator and checked against the paragraph its section number claims; a wrong section number fails the build in the same way a fabricated quotation does. Section numbers follow `01-product-design-structured.md`, the sectioned transcription — the source of truth itself carries no section numbers.

## How to read this file

- **Double quotes are verbatim quotations** from the source of truth and nothing else. Where a claim is mine rather than the design's it is plain prose with no quote marks.
- **Single quotes are pattern literals** — tokens a recogniser looks for in a document — following the convention in the contract's own worked example.
- `reliability_ceiling` uses §3.13's six states only. `direct` means a labeled field, a document title or explicit metadata. `validated` means a rule found a pattern **and** passed a context check, so every `validated` field has a matching `recognition.deterministic` line that could actually confirm it. `llm_supported` means the value needs language interpretation and cannot be produced without the model route.
- `sensitivity` is §2.9's phrase `potentially sensitive` and nothing more. No handling class is assigned anywhere in this file; handling classes are P7's (§8.4).
- No thresholds, no scores, no counts. Digits appear only inside `example` values, which are data in the same way the contract's own `BUSIB 4300` is.

## Five findings that apply to the whole slice

**1 — The design names no engineering domain, so this slice is almost entirely `proposal`.** The exemplar list is Academic, Applications, Research, Career / Recruiting, Photos, Travel and Financial. §3.11's field rows cover academic, application, research, finance, photo and code files and stop. §5.1's typical canvas has no engineering branch and §5.7's template-library list has no engineering entry. Three entries are marked `inference` because they extend something the design does name — CAD and 3D files in §2.9, and the universal `version family` fact in §3.11 — and the other forty-two are honest additions under §3.15's placeholder clause. There is no `design` row in this file and there should not be one.

**2 — Revision is a fact, never a folder level.** This is the slice's load-bearing decision and it is set out in full on `eng.drawing-package`. §3.1 makes "a member of a version family" a fact about a file; §3.11 makes `version family` one of the small set of UNIVERSAL file facts; §4.1 makes `version stems` a rules-engine output. So Rev A and Rev B of one drawing are one artifact at two states, the group's identity is the drawing number alone, and no domain in this file declares its own version field — declaring one would be a domain inventing a universal, which §3.12 forbids. Many entries carry a revision-shaped field — `revision`, `drawing_revision`, `parent_revision`, a `from_revision` and `to_revision` pair — and in every one of them it names the member's POSITION in the family and never the family itself. No `dimension_order` in this file contains a revision, because §5.9 warns against a level that produces only one child and a revision level does exactly that. Two exceptions are called out where they are real: calibration history and environmental monitoring are genuine time series rather than version families, because there the older member is not superseded.

**3 — The part number is this slice's over-firing pattern, and the title block is its syllabus.** §3.5's worked model is a course-code pattern *plus* academic context. The engineering transposition is a part-number or drawing-number pattern *plus* a title-block cluster — two or more of 'drawing no', 'rev', 'sheet _ of _', 'scale', 'drawn', 'checked', 'approved', 'material', 'finish', 'tolerances unless otherwise specified'. A bare alphanumeric code with a dash matches order numbers, invoice numbers, ZIP codes, git hashes, IMG filenames and standard numbers alike, which is §3.10's warning almost word for word. Every entry here puts the bare code in `never_alone`.

**4 — Nothing in this slice puts time first.** §5.5's exception is capture-based media, and there is none here. "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." Every `time_first` in this file is `false`, including the record domains where a year is a real level — it follows the site or the product rather than leading.

**5 — §8.4's corpus list does not reach this supercategory, and that is the finding rather than a failure to discriminate.** It names "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" and stops. It has no concept of commercial confidentiality, trade secrets, customer-confidential data or export-controlled technical data — the only restrictions anyone in this field actually works under. Read honestly, an unreleased product drawing is not sensitive and may take the cloud route while a payslip may not. Only seven entries below are marked `potentially_sensitive` (7 of 45), and each hooks onto a category §8.4 actually names: injury information, a regulator submission, an identified customer, GPS metadata, or a supplier's bank and tax details. The gap is raised as an open question on `eng.engineering-project` and sharpened on `eng.aerospace-airworthiness` and `cert.standards-library`. Nothing here invents a marking to close it.

## Index

| # | id | Domain | Provenance | Sensitivity | Open question |
|---|---|---|---|---|---|
| 1 | `eng.engineering-project` | Engineering project or programme (branch root) | proposal | none | yes |
| 2 | `eng.requirements-specification` | Requirements and engineering specifications | proposal | none | — |
| 3 | `eng.stage-gate-review` | Product development stage-gate reviews | proposal | none | — |
| 4 | `eng.industrial-design` | Industrial design, form and CMF | inference | none | — |
| 5 | `eng.cad-model` | CAD parts and assembly models | inference | none | — |
| 6 | `eng.drawing-package` | Engineering drawings under revision control | inference | none | yes |
| 7 | `eng.gdt-tolerance` | Tolerance analysis and GD&T | proposal | none | — |
| 8 | `eng.bill-of-materials` | Bills of materials | proposal | none | — |
| 9 | `eng.change-order` | Engineering change requests and orders | proposal | none | — |
| 10 | `eng.simulation-fea` | Simulation, FEA and CFD studies | proposal | none | — |
| 11 | `eng.electrical-schematic` | Electrical schematics and wiring design | proposal | none | — |
| 12 | `eng.pcb-layout` | PCB layout and fabrication packages | proposal | none | — |
| 13 | `eng.civil-structural` | Civil and structural design | proposal | none | — |
| 14 | `eng.process-flow-pid` | Chemical and process plant design | proposal | none | — |
| 15 | `eng.aerospace-airworthiness` | Aerospace type design and airworthiness data | proposal | none | yes |
| 16 | `eng.automotive-program` | Automotive vehicle programme and homologation | proposal | none | — |
| 17 | `eng.material-specification` | Material and process specifications | proposal | none | — |
| 18 | `eng.component-datasheet` | Component datasheets and vendor technical data | proposal | none | — |
| 19 | `eng.risk-analysis-fmea` | Design and process risk analysis | proposal | none | — |
| 20 | `eng.prototype-build` | Prototype builds, additive manufacturing and build records | proposal | none | — |
| 21 | `eng.verification-validation` | Test plans, protocols and validation reports | proposal | none | — |
| 22 | `eng.commissioning-handover` | Commissioning and handover packages | proposal | none | — |
| 23 | `eng.as-built-record` | As-built and record documentation | proposal | none | — |
| 24 | `eng.invention-disclosure` | Invention disclosures and technical patent material | proposal | potentially_sensitive | — |
| 25 | `cert.certification-file` | Product certification and conformity files | proposal | none | — |
| 26 | `cert.standards-library` | Standards and codes reference library | proposal | none | yes |
| 27 | `mfg.production-planning` | Production planning and scheduling | proposal | none | — |
| 28 | `mfg.work-instruction` | Work instructions and manufacturing SOPs | proposal | none | — |
| 29 | `mfg.production-record` | Production and batch records | proposal | none | — |
| 30 | `mfg.tooling-fixture` | Tooling, moulds and fixtures | proposal | none | — |
| 31 | `qual.management-system` | Quality management system documentation | proposal | none | — |
| 32 | `qual.inspection-record` | Inspection and measurement records | proposal | none | — |
| 33 | `qual.calibration-record` | Calibration and metrology records | proposal | none | — |
| 34 | `qual.nonconformance-capa` | Nonconformance and corrective action | proposal | none | — |
| 35 | `qual.failure-analysis-rca` | Failure analysis and root cause investigation | proposal | none | — |
| 36 | `qual.supplier-qualification` | Supplier qualification and audit | proposal | potentially_sensitive | — |
| 37 | `qual.warranty-claim` | Warranty claims and field-return analysis | proposal | potentially_sensitive | — |
| 38 | `mro.asset-record` | Asset register and equipment records | proposal | none | — |
| 39 | `mro.maintenance-work-order` | Maintenance work orders and history | proposal | none | — |
| 40 | `mro.spare-parts` | Spare parts and stock records | proposal | none | — |
| 41 | `mro.field-service-report` | Field service reports | proposal | potentially_sensitive | — |
| 42 | `hse.safety-case` | Safety cases and safety justification | proposal | potentially_sensitive | — |
| 43 | `hse.incident-record` | HSE incident and near-miss records | proposal | potentially_sensitive | yes |
| 44 | `hse.environmental-compliance` | Environmental permits and monitoring | proposal | potentially_sensitive | — |
| 45 | `hse.energy-audit` | Energy audits and efficiency surveys | proposal | none | — |

## Entries

## `eng.engineering-project` — Engineering project or programme (branch root)

Engineering, manufacturing and physical-trades material that carries a project or product identity but no more specific sub-domain — the branch itself.

**Provenance:** **proposal**

**Cite:** The design names no engineering, manufacturing or physical-trades domain anywhere. The exemplar list is Academic, Applications, Research, Career / Recruiting, Photos, Travel and Financial; §3.11's field rows cover academic, application, research, finance, photo and code files and stop; §5.1 "a typical initial canvas might include Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material" has no engineering branch; and §5.7 "covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections" has no engineering entry either. This whole slice therefore sits under §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Hawk Mk2 actuator | `validated` | §3.11 names project as a field for research files and for code files. Reusing the same field name here rather than inventing a parallel one is what §3.12 "The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically." requires. |
| `product` | string | Hawk Mk2 | `validated` | the marketed or delivered thing, as distinct from the project that produces it; §3.8 "The system must separate roles that happen to contain the same entity type." |
| `discipline` | string | mechanical | `validated` | the engineering discipline is this slice's nearest analogue to §3.11's academic `subject`, and it is the dimension that most often decides which sub-domain schema is plausible |
| `artifact_type` | string | specification | `validated` | §3.11's Research row names `artifact type`; this is the same field applied to engineering output |
| `lifecycle_stage` | string | detailed design | `validated` | §3.11's Research row names `stage`; a product programme has the same shape |
| `organisation` | string | Kestrel Dynamics | `validated` | recorded for search and explanation only. §3.8 "It should avoid using authorship or creator identity as a destination dimension." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a project or product token that already appears in a user-created folder name, co-occurring with an engineering artifact term in a document title or a page-one heading — 'drawing' | 'specification' | 'bill of materials' | 'test report' | 'work instruction' | 'calculation'
- a discipline term ('mechanical' | 'electrical' | 'structural' | 'process' | 'civil' | 'manufacturing') in a document title together with a document-control block — a document-number label together with a revision label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a report whose subject is plainly an engineering problem but which names no part, project, standard or drawing anywhere
- a folder of native design files whose project is stated only in prose inside a README-like note

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare alphanumeric code with a dash — this slice's single worst over-firing pattern. It has the same shape as an order number, an invoice number, a ZIP code, a git hash, an IMG filename and a standard number, and §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values."
- the word 'design' — as common in a marketing deck as on a drawing
- a CAD or ECAD extension alone: §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text", so the extension is §2.9's routing signal and never a domain fact

### Work types

`specification`, `drawing`, `report`, `calculation`, `schedule`, `presentation`, `correspondence`

### Grouping reasons (§4)

- one project across its design, build and test artifacts
- one product across one lifecycle stage
- one release across the documents issued together

### Template (§5)

`project → discipline → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child" — a discipline is only meaningful once the project is known, and an artifact type only once the discipline is. §5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." keeps time out of the order entirely, which is true of every entry in this slice.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| soft.source-project | an engineering project and a software project are the same word for two things. The separating signal is structural, not lexical: where §2.4's repository markers sit beside the files, the software slice's claim is the stronger one; where a title block, a change-order number or a released drawing does, this slice's is | §2.4 "structural indicators such as repository markers, package manifests, notebook metadata, and README files" |
| res.research-project | an engineering project and a research project have identical shape — a name, stages, artifacts and a team. The separating evidence is what the output is for: a released document-control block on one side, a manuscript, venue or grant on the other | §3.9 "The documents are content-incoherent but purpose-coherent." |
| acad.course-enrollment | a capstone or design-course project produces drawings, BOMs and test reports that are indistinguishable from professional ones; the corroboration that decides it is academic context, not engineering content | §3.5 "BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as" |
| pers.creative-project | a personal build — a workshop project, a restoration, a home-made machine — carries the same artifacts with no organisation behind them | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

### Open question — for Joseph, unresolved

THREE calls belong to Joseph and this slice cannot be finished without them. FIRST — WHOSE CORPUS IS THIS? §1.1 and §5.1 describe one person's Downloads, Desktop and Documents. Most engineering and manufacturing material is produced at work, owned by an employer and stored on a shared drive; a personal corpus holds only the fragments that reached the individual's machine. Every template below is written for the fragment case, which is the conservative reading. If employer, team or site corpora are in scope, `site` and `organisation` become real folder levels rather than metadata and roughly a third of the dimension orders here change. SECOND — §8.4'S CORPUS LIST DOES NOT REACH THIS SLICE. It names "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" and stops. It has no concept of commercial confidentiality, trade secrets, customer-confidential data or export-controlled technical data, which are the only restrictions anyone in this field actually operates under. Read honestly, an unreleased product drawing is not sensitive and may go to a cloud model, while a payslip may not. That is almost certainly not what is wanted, but the vocabulary for fixing it is P7's and not this catalogue's, so nothing here invents a marking: only seven of these entries are marked `potentially_sensitive`, and each hooks onto a category §8.4 actually names. THIRD — THERE IS NO TOP-LEVEL BRANCH FOR THIS SLICE. §5.1's typical canvas offers Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material. Engineering material either needs a branch of its own, or goes under Code and Projects (which would make `soft.*` and `eng.*` siblings and is defensible for a hardware start-up), or under Research (defensible in a lab). That is a default folder structure for someone's real working life and it is not mine to set.

---

## `eng.requirements-specification` — Requirements and engineering specifications

A document that states what a product, system or component must do, and how conformance will be shown.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." The software slice's `soft.technical-specification` is the same document shape for a different object; the collision is recorded below rather than resolved.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Hawk Mk2 actuator | `validated` | §3.11's project field, as on the branch root |
| `specified_item` | string | front actuator housing | `validated` | the thing the document constrains. This is the domain's subject and, per §5.5 "a parent dimension should provide the context required to understand the child", its second folder level |
| `document_number` | string | SPEC-HK2-014 | `validated` | the controlled identity. §3.13 "A validated fact was found by a deterministic rule and passed contextual checks" — the pattern alone is worthless here and the context check is the document-control block, not the number's shape |
| `revision` | string | C | `direct` | §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." — a revision label in a document-control block is such a field. It names this file's position in the §3.11 version family; it is not a separate artifact identity |
| `discipline` | string | mechanical | `validated` | as on the branch root |
| `baseline` | string | PDR baseline | `direct` | a labeled field in the control block where present; recorded for search and explanation |
| `approval_state` | string | approved | `direct` | read from a labeled signature or status block; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a document-control block — a document-number label ('document no' | 'spec no' | 'specification number') together with a revision label ('rev' | 'revision' | 'issue') — co-occurring with requirement language in headings: 'shall' used as a normative verb, 'verification method', 'acceptance criteria'
- a requirement-identifier column in a §2.3 table (a 'REQ-' style identifier under a 'requirement id' header) together with a verification-method or acceptance-criteria column in the same table

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a specification written as continuous prose with no requirement identifiers, whose specified item must be read from the introduction
- deciding whether a document specifies a physical item or a software component when both vocabularies appear in it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'shall' — the normative verb of contracts, policies, statutes and standards as much as of specifications
- a bare document number
- a requirement-identifier prefix on its own: 'REQ-014' appears in software backlogs, test-management exports and issue trackers

### Work types

`requirements specification`, `interface control document`, `performance specification`, `design specification`, `verification cross-reference matrix`, `specification change note`, `statement of work`

### Grouping reasons (§4)

- one specification across its issues — a §3.11 version family, not a set of separate documents
- one specified item across its specification, verification matrix and the tests that close it

### Template (§5)

`project → specified item → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child". §5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| soft.technical-specification | the same document shape describes a software component and a physical one, and both use 'shall', requirement identifiers and verification methods. The separating signal is what verification means: a rig, an inspection or a measurement here, a test suite or a code review there — never the word 'specification'. Where §2.4's repository markers sit beside the file, the software slice's claim is stronger | §2.4 "structural indicators such as repository markers, package manifests, notebook metadata, and README files" |
| soft.design-doc-rfc | an RFC and an engineering specification both state an intended design for review; the RFC is repository-resident and unreleased, the specification is document-controlled and issued | §3.11 "One file may hold facts from more than one domain without losing information." |
| cert.standards-library | a specification that is mostly a call-up of external standards looks like a standard; the separating signal is whether the document was authored here or received | §3.8 "The system must separate roles that happen to contain the same entity type." |
| legal.contracts | a specification attached to a supply agreement is a contract schedule and a specification at once | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.stage-gate-review` — Product development stage-gate reviews

The pack assembled to take a development programme through one decision gate, and the decision it produced.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Hawk Mk2 | `validated` | §3.11's project field |
| `gate` | string | PDR | `validated` | the gate identity. §3.13 "A validated fact was found by a deterministic rule and passed contextual checks" — a three-letter token needs the corroboration listed under recognition |
| `review_date` | string | 2026-03-11 | `direct` | a labeled date field; §3.10 "Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching." |
| `decision` | string | proceed with actions | `direct` | read from a labeled decision or outcome field |
| `artifact_type` | string | gate pack | `validated` | as on the branch root |
| `chair_role` | string | programme director | `direct` | the role, not the person: §3.8 "A folder should not become a collection point for everything produced by the same person or organization." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a gate name ('gate 2' | 'PDR' | 'CDR' | 'design review' | 'phase review' | 'tollgate') in a document title together with a decision or action block — 'gate outcome' | 'decision' | 'actions arising' | 'exit criteria'
- an exit-criteria table (§2.3) whose headers pair a criterion column with a met / not-met column, together with a project name in the title or the header row

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- minutes that record a gate decision without ever naming the gate
- deciding whether a review was a gate or a routine technical peer review, which produce the same minutes

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- 'design review' alone — a design review is also the routine peer review that happens between gates
- a date in a title
- an exit-criteria table with no project: every audit and inspection in this slice has one

### Work types

`gate pack`, `exit-criteria checklist`, `review minutes`, `action log`, `decision record`, `deviation request`, `readiness assessment`

### Grouping reasons (§4)

- one gate across its pack, minutes, actions and decision
- one project across its successive gates — the only sequence in this slice where order matters more than identity

### Template (§5)

`project → gate → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child" — a gate name means nothing without its programme.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.change-order | a gate that authorises a design change is both the gate record and the change authority | §3.11 "One file may hold facts from more than one domain without losing information." |
| soft.architecture-decision-record | both record a decision with its reasoning and its alternatives; the ADR is repository-resident and per-decision, the gate pack is programme-resident and per-milestone | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.verification-validation | gate evidence is largely test evidence, and the same report is cited in both places | §3.11 "One file may hold facts from more than one domain without losing information." |
| corp.compliance-audit | a gate review and a compliance audit share the finding-and-action document shape exactly | §3.8 "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.industrial-design` — Industrial design, form and CMF

Work on how a product looks and feels — sketches, renders, colour-material-finish boards and appearance models.

**Provenance:** **inference**

**Cite:** Extends a design-named file class rather than a design-named domain: §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" names the creative-format family and states exactly what the evidence layer may take from it. The domain built on it is an addition; §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Hawk Mk2 | `validated` | §3.11's project field |
| `product` | string | Hawk handset | `validated` | the appearance work's subject |
| `variant` | string | graphite colourway | `validated` | the CMF or form variant this file belongs to |
| `material_finish` | string | bead-blasted anodise | `validated` | the CMF half of the domain, and a search field |
| `artifact_type` | string | render | `validated` | as on the branch root |
| `canvas_properties` | string | 3840 x 2160 | `direct` | §2.9 promises exactly this for design formats: §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a §2.9 design-format or image file whose parent-folder context names a product, together with an appearance term in the filename or a slide title — 'render' | 'CMF' | 'colourway' | 'appearance model' | 'form study' | 'moodboard'
- a presentation whose slide titles pair a product name with 'concept' | 'form exploration' | 'material study', and whose §2.9 design-format siblings share the same product token

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a render that is indistinguishable from a marketing image without reading the deck it sits in
- separating a concept sketch from unrelated personal artwork in the same folder

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a design-format extension — §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text", which cannot establish a product
- a colour or material name
- the word 'concept'

### Work types

`concept sketch`, `render`, `CMF board`, `moodboard`, `form study`, `appearance model specification`, `packaging visual`, `design review deck`

### Grouping reasons (§4)

- one product across one concept round
- one colourway across its boards, renders and material samples
- one render across its exported sizes — a duplicate family rather than a version family

### Template (§5)

`project → product → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.creative-project | personal art and product concept work live in the same formats, and §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" gives neither readable text. The separating evidence is external: a product token that also appears in a BOM, a drawing or a gate pack | §2.9 "unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty" |
| eng.cad-model | the appearance model and the engineering model are frequently the same geometry serving two purposes | §3.9 "The documents are content-incoherent but purpose-coherent." |
| career.portfolio | the same render appears in the designer's portfolio; the file is one artifact with two purposes | §3.11 "One file may hold facts from more than one domain without losing information." |
| soft.game-development-asset | 3D assets, texture maps and render outputs are format-identical | §2.9 "unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty" |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.cad-model` — CAD parts and assembly models

Native geometry — the model a physical thing is derived from, before and beside the drawing that releases it.

**Provenance:** **inference**

**Cite:** Extends a design-named file class. §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" — the design names CAD files and 3D files explicitly and states exactly what may be extracted from them, including the linked asset names this domain's structural recognition depends on. The domain itself is an addition; §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Hawk Mk2 actuator | `validated` | §3.11's project field |
| `part_number` | string | HK2-4471-01 | `validated` | the model's identity. §3.13 "A validated fact was found by a deterministic rule and passed contextual checks" — and the context check is severe here, because a part number has the same shape as everything §3.10 warns about |
| `part_name` | string | housing, front | `direct` | §2.9 promises "embedded metadata" for CAD files, and a populated title property is §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `model_type` | string | assembly | `validated` | part, assembly, drawing-linked or neutral export — the structural role of the file |
| `cad_format` | string | STEP AP242 | `direct` | §2.9 "the file extension as a routing signal rather than an assumption about meaning", corroborated by the real MIME type or file signature where one exists |
| `linked_assets` | list of strings | HK2-4471-02, HK2-4471-03 | `direct` | §2.9 names this exactly: §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text". An assembly that references parts is structural evidence, not a filename guess |
| `revision` | string | B | `direct` | where the model carries a revision property. Its meaning is the file's position in the §3.11 version family, nothing more; §3.11 "The product should have a small shared set of universal file facts, such as file type, creation date, language, duplicate family, version family, and sensitivity status." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a CAD extension whose §2.9 embedded metadata carries a part-number or title property, together with a sibling set sharing the same part-number stem
- a CAD extension together with §2.9 linked asset names that resolve to files in the same folder — an assembly referencing its parts is a structural family, which §4.2 "A seed may be a strongly identified file, a validated shared fact, a structural family, or a user-created starting point."
- a part-number pattern in a filename co-occurring with a released drawing PDF of the same stem that carries a title block

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an unreadable proprietary model whose only project signal is prose in a neighbouring note
- deciding whether a downloaded STEP or STL is a work part or a hobby print

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a CAD or mesh extension on its own — §2.9 "unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty", so the extension routes and never concludes
- a bare part-number-shaped filename
- the presence of a 3D format: STL, OBJ, STEP and 3MF are as common in a hobby print folder as in an engineering release

### Work types

`part model`, `assembly model`, `neutral exchange file`, `mesh export`, `sheet-metal flat pattern`, `surface model`, `skeleton or master model`, `configuration table`

### Grouping reasons (§4)

- one assembly across the part models it references — §2.9's linked asset names make this deterministic
- one part number across its native model, neutral export and released drawing
- one model across its §3.11 version family

### Template (§5)

`project → assembly → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child" — a part model is meaningful once its assembly is known. Revision is deliberately absent; see `eng.drawing-package`, where the argument is set out in full.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.hobby-collection | a downloaded STL for a hobby print and a released engineering mesh are the same file shape, and §2.9 "unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty" means there is often no readable content either way. The separating evidence is entirely external: a part number that also appears in a title block, a BOM row or a change order, versus a model that sits beside slicer output in a print folder | §3.11 "One file may hold facts from more than one domain without losing information." |
| soft.hardware-design-file | the software slice already claims mechanical models as a work type. Where §2.4's repository markers sit beside the file, its claim is the stronger one; where a title block, a change-order number or a BOM row does, this one's is | §2.4 "structural indicators such as repository markers, package manifests, notebook metadata, and README files" |
| eng.drawing-package | the model and the drawing are one part at two representations; only the drawing is released and revision-controlled | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.industrial-design | the appearance model and the engineering model are often one file | §3.9 "The documents are content-incoherent but purpose-coherent." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.drawing-package` — Engineering drawings under revision control

One drawing number, one title block, and every state that drawing has passed through — a version family, not a set of documents.

**Provenance:** **inference**

**Cite:** Extends two design-named things. §3.1 "a member of a version family, and potentially sensitive" makes version-family membership a fact about a file; §3.11 "The product should have a small shared set of universal file facts, such as file type, creation date, language, duplicate family, version family, and sensitivity status." makes it universal; and §4.1 "The rules engine supplies the hard facts and the domain information: document type, course codes, dates, target institutions, project identifiers, duplicate relationships, version stems, capture metadata, filename patterns, and structural links." makes the stems a rules-engine output. This domain is that machinery applied where revision control is most formal. The domain itself is an addition; §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `drawing_number` | string | HK2-4471-01 | `validated` | the family's identity — the thing that is stable across every revision. §3.13 "A validated fact was found by a deterministic rule and passed contextual checks", and the context check is the title block described under recognition |
| `title` | string | HOUSING, FRONT | `direct` | the title-block TITLE field. §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `revision` | string | C | `direct` | the title-block REV field. §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.". Its meaning is precise and narrow: it names this file's POSITION in the §3.11 version family the drawing number identifies. Rev A and Rev B of one drawing are one artifact at two states, not two artifacts, and this field is the only thing that distinguishes them |
| `sheet` | string | 2 of 5 | `direct` | the title-block SHEET field; sheets are members of the same document, not versions of it |
| `project` | string | Hawk Mk2 actuator | `validated` | §3.11's project field |
| `discipline` | string | mechanical | `validated` | the title-block discipline field or the drawing-number prefix, corroborated |
| `scale` | string | 1:2 | `direct` | the title-block SCALE field; a search and explanation field, never a folder dimension |
| `approval_state` | string | released | `direct` | read from the title-block signature row ('drawn' / 'checked' / 'approved') or a release stamp; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a title-block cluster: a drawing-number label ('drawing no' | 'dwg no' | 'part no' | 'document number') together with at least one more title-block label from 'rev' | 'revision' | 'sheet _ of _' | 'scale' | 'drawn' | 'checked' | 'approved' | 'material' | 'finish' | 'tolerances unless otherwise specified' | 'third angle projection'. This is §3.5's model transposed: the pattern is the drawing number and the corroborating context is the title block, exactly as §3.5 "BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as"
- a §2.3 table extraction returning a title-block row — drawing number, revision, sheet and scale in adjacent cells. §2.3 "Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs."
- a drawing-number stem shared across several files whose only difference is a revision token, together with one title block anywhere in the set — this is §4.1 "The rules engine supplies the hard facts and the domain information: document type, course codes, dates, target institutions, project identifiers, duplicate relationships, version stems, capture metadata, filename patterns, and structural links."

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned legacy drawing whose title block OCRs badly and whose discipline must be read from the drawing content
- a sketch carrying a drawing number but no title block, where only the surrounding set shows whether it was ever released
- deciding which of two same-numbered files is the later issue when neither revision field survived the scan

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare revision token — 'Rev B', 'B', 'issue 2', '-02', 'v3'. This is the domain's own worst over-firing pattern: it appears in report filenames, contract drafts, resume versions and firmware tags, and on its own it identifies neither a drawing nor which drawing. A revision token corroborates a drawing number; it never establishes one
- a drawing-number-shaped code. §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." — a drawing number has the same shape as every item on that list
- 'sheet 1 of 3' alone — pagination language appears in reports, contracts and manuals
- a DWG or DXF extension: §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text", and none of that is a title block

### Work types

`detail drawing`, `assembly drawing`, `general arrangement`, `installation drawing`, `weldment drawing`, `sheet-metal flat`, `drawing list or register`, `revision-cloud markup`, `plotted scan`

### Grouping reasons (§4)

- one drawing number across every revision of it. This is a §3.11 version family and NOT a set of separate artifacts. §4.1 "The rules engine supplies the hard facts and the domain information: document type, course codes, dates, target institutions, project identifiers, duplicate relationships, version stems, capture metadata, filename patterns, and structural links." supplies the stems that find it, and the group's identity is the drawing number alone — the revision is a property of each member
- one drawing set across its sheets: one document number, sheet 1..n. Sheets are co-members, not versions, and the two relations must not be conflated — a set of five sheets at Rev C is one family with five members, not five families
- one release across the drawings, bill of materials and change order issued together
- one drawing across its native CAD source, released PDF and plotted scan — a duplicate or derived set rather than a version family

### Template (§5)

`project → discipline → assembly → artifact type`

Time first: **no**

REVISION IS DELIBERATELY ABSENT FROM THIS ORDER, and that is the load-bearing decision in this entry. §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." — a revision level produces exactly one child for every drawing that has had one revision, and a directory of near-identical folders for every drawing that has had many. The principle underneath it is §3.14 "Facts remain separate from the future destination tree." The revision is a fact about a member of a §3.11 version family; the folder holds the family. The design already has its own handling for the superseded member — §8.3 "retain the newer file while placing an older version into a version family review" — which is a review state, not a directory, and a domain that invented an `Obsolete/` folder would be creating a destination outside the frozen tree. The rest of the order follows §5.5 "a parent dimension should provide the context required to understand the child". See the open question: some regulated industries genuinely do file by revision, and that call is not mine.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.cad-model | the released drawing and the model it was made from share a part number and nothing else | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.change-order | the change order names the drawing and the drawing's revision history names the change order; they point at each other and neither owns the other | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.as-built-record | an as-built is a marked-up drawing. Some organisations treat it as another member of the same version family and some as a separate document class, and nothing in the file decides which | §3.11 "One file may hold facts from more than one domain without losing information." |
| pers.scanned-document | a scanned legacy drawing is a scan before it is a drawing, and if the title block does not OCR it stays one | §2.7 "OCR should therefore run when a file yields no usable text and no usable metadata, including scanned PDFs, confirmed screenshots, and opaque images without EXIF." |
| eng.electrical-schematic | a schematic sheet has a title block and a drawing number and is a drawing in every structural sense; this domain is the general schema and the discipline domains the specific ones | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

### Open question — for Joseph, unresolved

MAY A REVISION EVER BECOME A FOLDER LEVEL? This catalogue says no and files the family, not the state, for the reasons set out in the template rationale. But in regulated manufacture — aerospace type design, medical devices, nuclear, pressure equipment — superseded revisions must be retained, must be physically separable from the current issue, and must be provably not usable at the workstation; organisations there genuinely do file `.../DRAWING-NUMBER/Rev A | Rev B | Current`. §5.9's one-child warning argues against it and the retention obligation argues for it, and the answer decides the default folder structure of someone's real working life. Not mine. A SECOND QUESTION RIDES ON IT: when a file's title block says Rev C and a PLM or ERP export says Rev C is superseded, which is the fact? The design has no concept of an external system of record, and §3.13's `direct` state would let the title block win because it is a labeled field — which is wrong in every organisation that runs PLM. Either `revision` needs a companion `currency` fact sourced outside the file, or the product must decline to assert currency at all. I have written the schema so it asserts only what the file says.

---

## `eng.gdt-tolerance` — Tolerance analysis and GD&T

What variation a fit can absorb, argued for a specific characteristic on a specific assembly.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Hawk Mk2 actuator | `validated` | §3.11's project field |
| `assembly` | string | front housing stack | `validated` | the assembly whose variation is being argued |
| `characteristic` | string | bore-to-face perpendicularity | `validated` | the specific thing being controlled — this domain's subject, and what makes one study distinct from another |
| `analysis_method` | string | worst case | `validated` | worst-case, statistical or Monte Carlo; a labeled choice in the worksheet header |
| `datum_scheme` | string | A\|B\|C | `llm_supported` | §3.13 "An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation." — a datum scheme stated in a drawing note rather than a feature-control frame needs interpretation |
| `part_number` | string | HK2-4471-01 | `validated` | the part the callout lives on; corroborated as in `eng.drawing-package` |
| `artifact_type` | string | tolerance stack-up | `validated` | as on the branch root |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a GD&T vocabulary cluster in extracted text or a §2.3 table — two or more of 'datum' | 'MMC' | 'LMC' | 'true position' | 'profile of a surface' | 'runout' | 'perpendicularity' | 'flatness' — together with a part-number or drawing-number token in a title or header cell
- a stack-up worksheet: a §2.9 spreadsheet whose column headers pair a nominal column with a tolerance column and a contribution or direction column, together with a part-number token in a labeled cell. §2.9 "Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells."

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a tolerance argument written as prose inside a design report
- a datum scheme described in words and never tabulated
- deciding whether a variation study is dimensional tolerance or process capability — the arithmetic is the same

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a plus-or-minus symbol or a tolerance-shaped numeric pair — it appears in every datasheet, test report and quotation in this slice
- the word 'datum' — also a survey term, a database term and ordinary English
- a bare part number

### Work types

`tolerance stack-up`, `GD&T scheme`, `datum-scheme note`, `fit analysis`, `functional gauge definition`, `tolerance allocation study`, `variation simulation report`

### Grouping reasons (§4)

- one characteristic across its stack-up, its drawing callout and the inspection result that closes it
- one assembly across the tolerance studies done on it

### Template (§5)

`project → assembly → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.drawing-package | the callout lives on the drawing and the analysis lives beside it; the drawing number is in both | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.inspection-record | the measured result closes the predicted stack, and the numbers are the same numbers. What separates them is what the document is for: a prediction about a design, or evidence about a produced item | §3.9 "The documents are content-incoherent but purpose-coherent." |
| eng.simulation-fea | variation simulation is simulation, and the tool output is indistinguishable | §3.11 "One file may hold facts from more than one domain without losing information." |
| mfg.tooling-fixture | a functional gauge is defined by the tolerance scheme and built as a fixture | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.bill-of-materials` — Bills of materials

The structured parent-child list of what a product is made of, at one parent revision.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." The extraction path it depends on is design-named: §2.9 "Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `parent_part_number` | string | HK2-4471-00 | `validated` | the BOM's identity is the parent it explodes, not any of its lines |
| `parent_revision` | string | C | `direct` | a labeled header field. A BOM at Rev C and the same BOM at Rev D are one §3.11 version family, exactly as with drawings |
| `bom_type` | string | manufacturing | `validated` | engineering, manufacturing, as-built or costed — these are genuinely different documents about one product |
| `product` | string | Hawk Mk2 | `validated` | the marketed thing the parent belongs to |
| `effectivity` | string | from serial 0120 | `direct` | a labeled effectivity or from-date field where present |
| `source_system` | string | PLM export | `direct` | recorded because it changes how the file should be read; §2.2 "PDF metadata should be treated as supporting evidence, not as truth." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a §2.9 spreadsheet or §2.3 table whose column headers include a level or find-number column TOGETHER WITH a part-number column TOGETHER WITH a quantity column. The three-header cluster is what makes it a bill of materials rather than a parts list, a stock report or a purchase order — no one of the three is sufficient
- a level-indented part-number column (1, 1.1, 1.2) together with a parent part number in a labeled header cell
- a bill-of-materials label ('bill of materials' | 'parts list' | 'BOM') in a sheet name or document title together with a part-number column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a supplier quotation that is a de-facto BOM laid out as a price list
- deciding whether a parts list is the engineering BOM, the manufacturing BOM or a purchasing extract — the rows are the same and only the intent differs

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a quantity column — every invoice, order, packing list and stock report in this catalogue has one
- the token 'BOM' — in text-file evidence it is also a byte-order mark, and it is a common abbreviation elsewhere
- a part-number column with no parent and no level column: that is a catalogue, not a bill of materials

### Work types

`engineering bill of materials`, `manufacturing bill of materials`, `as-built bill of materials`, `BOM comparison or delta`, `where-used report`, `long-lead item list`, `costed bill of materials`

### Grouping reasons (§4)

- one parent part across its BOM revisions — a §3.11 version family whose members differ by parent revision
- one product across its engineering and manufacturing BOMs, which are different documents and not versions of each other
- one release across the BOM, drawings and change order issued together

### Template (§5)

`project → product → artifact type`

Time first: **no**

the parent part number is the BOM's identity but not a good folder level: one directory per part number is §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.drawing-package | an assembly drawing carries a parts list in its title-block area; the same rows exist in two documents | §3.11 "One file may hold facts from more than one domain without losing information." |
| mro.spare-parts | a recommended-spares list is a filtered BOM with a stock column added | §3.11 "One file may hold facts from more than one domain without losing information." |
| biz.procurement-po | a purchasing extract of the same rows. §3.8 "The system must separate roles that happen to contain the same entity type." — the supplier of a line and the manufacturer of the part are different roles of one entity type and must not collapse | §3.8 "The system must separate roles that happen to contain the same entity type." |
| soft.hardware-design-file | the software slice already names 'bill of materials' among its work types | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.change-order` — Engineering change requests and orders

A controlled request to change a released design, and the record of what was decided and implemented.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `change_number` | string | ECO-2026-0118 | `validated` | the change's identity; corroborated as under recognition |
| `affected_part` | string | HK2-4471-01 | `validated` | what the change touches. A change with no affected item is not a change order, which makes this the domain's real context check |
| `from_revision` | string | B | `direct` | a labeled from-field. Together with `to_revision` it is the link between two members of one §3.11 version family |
| `to_revision` | string | C | `direct` | a labeled to-field |
| `status` | string | approved | `direct` | a labeled disposition or status field; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `change_class` | string | form, fit and function | `validated` | whether the change is interchangeable — the distinction that decides effectivity and retrofit |
| `effectivity` | string | from serial 0120 | `direct` | a labeled effectivity field |
| `project` | string | Hawk Mk2 actuator | `validated` | §3.11's project field |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a change-number label ('ECO' | 'ECN' | 'ECR' | 'change request no' | 'MOC no' | 'change notice') together with an affected-item block — a part-number or drawing-number field beside a from/to revision pair
- a disposition block ('disposition' | 'approved' | 'rejected' | 'implemented' | 'change board') co-occurring with a change number in the document title
- a from/to revision pair in adjacent §2.3 table cells together with a part number in the same row. §2.3 "Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs."

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an email chain that agrees a change without one ever being raised
- distinguishing a change order from a deviation or a concession: the three share a document shape and mean quite different things about whether the design actually moved

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- 'ECO' — also a marketing prefix ('eco mode', 'eco pack') and a common filename fragment
- a from/to revision pair with no part number: every controlled document has a document-history table of that shape
- a bare change number

### Work types

`change request`, `change order or notice`, `impact assessment`, `deviation or concession`, `disposition record`, `implementation plan`, `change board minutes`, `retrofit instruction`

### Grouping reasons (§4)

- one change across its request, impact assessment, board minutes and disposition
- one affected part across every change ever raised against it
- one effectivity point across the changes released together

### Template (§5)

`project → artifact type`

Time first: **no**

one folder per change number is §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." The change number is a fact and a filename; the folder holds the project's change record. This is the same argument as the revision argument on `eng.drawing-package`.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.drawing-package | the change order and the drawing revision are two records of one event | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.bill-of-materials | most changes are BOM changes and the impact assessment is a BOM delta | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.nonconformance-capa | a corrective action that resolves into a design change: the nonconformance records the defect and the change order records the fix, and both carry the same part number and the same date | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.stage-gate-review | a gate that authorises a change is both records at once | §3.11 "One file may hold facts from more than one domain without losing information." |
| mfg.work-instruction | a change that only touches the instruction never reaches a drawing | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.simulation-fea` — Simulation, FEA and CFD studies

A computed prediction of physical behaviour, with the model it came from and the load case it answers.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Hawk Mk2 actuator | `validated` | §3.11's project field |
| `analysed_item` | string | front housing | `validated` | the thing the study is about — this domain's subject |
| `analysis_type` | string | structural static | `validated` | structural, modal, thermal, fatigue, CFD; a labeled or headed field |
| `load_case` | string | 2.5g down, hot day | `validated` | the specific condition analysed. One item and five load cases is five studies, which makes this the field that actually distinguishes members |
| `solver` | string | Abaqus 2025 | `direct` | §2.9 promises embedded metadata for these formats and a solver-written header is §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `model_revision` | string | rev 4 mesh | `direct` | a labeled model or mesh version field where present |
| `artifact_type` | string | analysis report | `validated` | as on the branch root |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- an analysis-type term ('FEA' | 'finite element' | 'CFD' | 'modal analysis' | 'thermal analysis' | 'stress analysis') in a document title together with a load-case or boundary-condition heading — 'load case' | 'boundary conditions' | 'constraints' | 'material model' | 'mesh convergence'
- a solver-written result or input file whose §2.9 embedded metadata names a model, together with a sibling report that carries the same analysed-item token
- a results table whose headers pair a load-case column with a margin, factor-of-safety or utilisation column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a report presenting contour plots and a conclusion that never names the analysis type
- deciding whether a computed result is an engineering prediction closing a requirement or a research simulation answering a question — the solver, the mesh and the plots are identical

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a contour-plot image — the most recognisable and least conclusive artifact in this domain
- the word 'model': this slice uses it for geometry, material models, simulation models and business models
- a solver name alone — solver names appear in CVs, training material and procurement documents

### Work types

`analysis report`, `model input deck`, `mesh file`, `result set`, `load-case definition`, `correlation report`, `hand calculation`, `convergence study`

### Grouping reasons (§4)

- one analysed item across its load cases
- one model across its input deck, results and report
- one design iteration across the analysis that predicted it and the test that correlated it

### Template (§5)

`project → analysed item → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.analysis-code | an engineering simulation and a research simulation are the same artifact produced by the same tools. What separates them is what the result is for — closing a design requirement, or answering a research question — and that is never in the result file | §3.9 "The documents are content-incoherent but purpose-coherent." |
| soft.notebook-analysis | post-processing notebooks sit in both slices and carry repository markers | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.verification-validation | the correlation report belongs to the analysis and to the test at once | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.civil-structural | a structural calculation is an analysis; the civil domain is the discipline-specific schema | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.electrical-schematic` — Electrical schematics and wiring design

Circuit, control and power design on paper — schematic sheets, wiring diagrams, harnesses and panel drawings.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Hawk Mk2 actuator | `validated` | §3.11's project field |
| `system` | string | actuator control loop | `validated` | the circuit or system the sheet belongs to |
| `drawing_number` | string | HK2-E-2201 | `validated` | as in `eng.drawing-package`; the same title-block corroboration applies |
| `revision` | string | B | `direct` | the title-block REV field; a position in a §3.11 version family |
| `sheet` | string | 3 of 12 | `direct` | the title-block SHEET field |
| `voltage_class` | string | low voltage | `validated` | extra-low, low or high voltage — a safety-relevant distinction and a search field |
| `artifact_type` | string | wiring diagram | `validated` | as on the branch root |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- an ECAD or schematic file whose sibling released PDF carries a title block, together with a schematic vocabulary cluster — two or more of 'net' | 'reference designator' | 'wire number' | 'terminal' | 'schematic sheet' | 'from-to'
- a reference-designator table in a §2.3 table or §2.9 spreadsheet — a designator column beside a value or part-number column — together with a drawing number
- a wiring schedule: a from-terminal column beside a to-terminal column beside a wire-number column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a hand-drawn or scanned circuit whose system must be read from the drawing content
- distinguishing a control schematic from a power single-line when neither carries a discipline label

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a reference-designator-shaped token — 'R1', 'C4', 'U2' also match spreadsheet cell references, room numbers and clause numbers, and §3.7 "It should use word-boundary matching rather than substring matching."
- an ECAD extension — §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text", which is not a schematic
- the word 'circuit'

### Work types

`schematic sheet`, `single-line diagram`, `wiring diagram`, `harness drawing`, `panel layout`, `terminal schedule`, `cable schedule`, `loop drawing`, `interconnect list`

### Grouping reasons (§4)

- one circuit across its schematic sheets — co-members of one document, not versions
- one drawing number across its revisions, which is a §3.11 version family
- one panel across its schematic, layout and terminal schedule

### Template (§5)

`project → system → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.pcb-layout | the schematic and the board are one design at two stages and share every reference designator | §3.11 "One file may hold facts from more than one domain without losing information." |
| soft.hardware-design-file | the software slice already names 'schematic' among its work types | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.civil-structural | building-services drawings are electrical and structural at once, in one drawing register | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.drawing-package | an electrical drawing is a drawing: this domain is the discipline-specific schema and `eng.drawing-package` the general one, and a file legitimately carries both | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.pcb-layout` — PCB layout and fabrication packages

The physical realisation of a circuit on a board, and the manufacturing package produced from it.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." Its strongest recognition route is design-named: §2.5 "The engine should read and store the archive type, contained paths, filenames, folder names, extensions, file count, uncompressed size where available, and recognizable markers such as source-code manifests or document names."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Hawk Mk2 actuator | `validated` | §3.11's project field |
| `board_name` | string | HK2-MAIN | `validated` | the board's identity, which is usually a job name rather than a part number |
| `board_revision` | string | B | `direct` | a labeled revision field in the fabrication notes or the silkscreen text; a position in a §3.11 version family |
| `layer_stackup` | string | four layer, controlled impedance | `validated` | a labeled stack-up field; it decides who can build the board |
| `assembly_variant` | string | populated, export build | `validated` | one board, several build variants — the field that distinguishes co-members |
| `fabrication_package` | string | Gerber X2 plus drill plus centroid | `direct` | read from the §2.5 archive manifest without unpacking it: §2.5 "the normal scan should never extract archive contents to the filesystem, because doing so creates security, storage, and side-effect risks" |
| `cad_format` | string | Altium PcbDoc | `direct` | §2.9 "the file extension as a routing signal rather than an assumption about meaning" |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a fabrication-package archive read through §2.5 whose contained paths include Gerber layer names TOGETHER WITH a drill file TOGETHER WITH a pick-and-place or centroid file. The co-occurrence of the three file classes inside one manifest is the corroboration; no one of them alone is
- a board-file extension together with a sibling bill of materials whose part-number column carries reference designators
- a fabrication-notes sheet ('layer stackup' | 'fab notes' | 'impedance control' | 'solder mask' | 'surface finish') together with a board name in the title

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a bare Gerber set with no readable job name anywhere in the manifest
- deciding whether a board design is a product or a personal project — the file set is identical

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a Gerber-style extension on its own
- a reference designator
- the word 'board' — this slice also uses it for change boards, review boards and material review boards

### Work types

`board layout`, `fabrication package`, `drill file`, `pick-and-place file`, `stack-up note`, `assembly drawing`, `impedance report`, `panel or array drawing`, `test-point report`

### Grouping reasons (§4)

- one board across its layout, fabrication package and assembly BOM — §2.5 reads the archive manifest without unpacking it
- one board name across its revisions, a §3.11 version family
- one product across its board, its firmware and its enclosure

### Template (§5)

`project → board → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| soft.hardware-design-file | the software slice already names 'board layout' and 'fabrication output' among its work types | §3.11 "One file may hold facts from more than one domain without losing information." |
| soft.embedded-firmware | the firmware and the board are one product held in two domains, and they share a repository as often as not | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.electrical-schematic | schematic and layout are one design at two stages | §3.11 "One file may hold facts from more than one domain without losing information." |
| pers.hobby-collection | a hobby board produces exactly this file set, with the same tools and the same names | §2.9 "unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty" |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.civil-structural` — Civil and structural design

Design of fixed works — buildings, bridges, foundations, drainage — and the calculations that justify them.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Bramley Street footbridge | `validated` | §3.11's project field |
| `structure` | string | north abutment | `validated` | the element or structure the document is about |
| `discipline` | string | structural | `validated` | civil, structural, geotechnical or drainage — these run as separate drawing registers |
| `drawing_number` | string | BSF-S-1204 | `validated` | as in `eng.drawing-package` |
| `revision` | string | P03 | `direct` | the title-block REV field; preliminary and construction issue series are members of one §3.11 version family |
| `design_code` | string | Eurocode 2 | `validated` | the code the calculation is to. Jurisdiction-dependent — see the open question on `eng.engineering-project` |
| `site` | string | Bramley Street | `validated` | the physical location; a search field, and a folder level only where a corpus spans sites |
| `design_stage` | string | detailed design | `validated` | §3.11's Research row names `stage`; the same field applied to a construction programme |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a design-code citation ('Eurocode' | 'BS EN' | 'ACI' | 'AISC' | 'AS/NZS') in a calculation heading together with a structural element term — 'slab' | 'beam' | 'pile' | 'foundation' | 'retaining wall' | 'abutment'
- a title block (recognised as in `eng.drawing-package`) whose discipline field or drawing-number prefix carries a civil or structural token, together with a grid-reference or level annotation
- a calculation sheet whose §2.3 table pairs a load or action column with a capacity or resistance column and a utilisation column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a structural narrative in a report with no calculation tables and no code citation
- deciding whether a survey drawing shows existing conditions or proposed works
- reading a hand calculation photographed from a notebook

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a design-code number — a standard number matches every other standard number in this slice, and §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values."
- a structural element word: 'beam' and 'slab' appear in optics, publishing and cookery
- a site address, which belongs as readily to a property record as to a design package

### Work types

`general arrangement`, `reinforcement detail`, `structural calculation`, `design statement`, `temporary-works design`, `setting-out drawing`, `geotechnical interpretative report`, `schedule of quantities`, `site investigation report`

### Grouping reasons (§4)

- one structure across its general arrangement, details and calculations
- one drawing number across its revision series — a §3.11 version family in which a preliminary and a construction issue are members, not separate drawings
- one site across the packages issued for it

### Template (§5)

`project → structure → discipline → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.as-built-record | the record drawing and the design drawing carry one drawing number between them | §3.11 "One file may hold facts from more than one domain without losing information." |
| pers.home-tenure | a householder's extension drawings, structural calculations and building-control correspondence are civil design and a property record simultaneously, and the file cannot tell you which life it belongs to | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.commissioning-handover | the handover pack contains the whole design package as issued | §3.9 "The documents are content-incoherent but purpose-coherent." |
| hse.safety-case | temporary works design and construction-phase safety material sit in both | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.process-flow-pid` — Chemical and process plant design

How material and energy move through a plant, and the instrumented control of that movement.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Unit 400 debottleneck | `validated` | §3.11's project field |
| `plant_unit` | string | Unit 400 | `validated` | the process unit — this domain's subject and its second folder level |
| `drawing_number` | string | U400-PID-0032 | `validated` | as in `eng.drawing-package` |
| `revision` | string | 4 | `direct` | the title-block REV field; a position in a §3.11 version family |
| `process_stage` | string | front-end engineering design | `validated` | concept, FEED, detailed or as-built — the same `stage` field §3.11 names for research files |
| `service_fluid` | string | wet process gas | `validated` | what is in the line; a search and safety field |
| `artifact_type` | string | P&ID | `validated` | as on the branch root |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- an equipment-tag pattern (a letter-prefixed vessel, pump or exchanger tag) co-occurring with a process vocabulary cluster — two or more of 'P&ID' | 'process flow diagram' | 'stream' | 'line list' | 'utility' | 'battery limit'
- an instrument-tag pattern (a loop-typed tag such as a flow, level or pressure indicator) together with a loop-number or line-number column in a §2.3 table
- a heat-and-material-balance table pairing a stream column with temperature, pressure and flow columns, together with a unit name in the header

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a process description written in prose with no diagram, tag list or balance table
- distinguishing a concept sketch from a released P&ID when the title block did not scan
- deciding whether a tag names process equipment or a maintenance asset — in most plants it is the same string

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an equipment tag alone — the same shape as a drawing number, an order number and a room number
- the word 'stream', which this catalogue also uses for data
- 'P&ID' inside a document that merely references one, which every procedure in the plant does

### Work types

`process flow diagram`, `P&ID`, `heat and material balance`, `line list`, `equipment list`, `instrument index`, `equipment datasheet`, `cause-and-effect matrix`, `hazardous-area classification drawing`

### Grouping reasons (§4)

- one unit across its PFD, P&ID, line list and equipment list
- one drawing number across its revisions, a §3.11 version family
- one plant across one design stage

### Template (§5)

`project → plant unit → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.electrical-schematic | loop drawings and cause-and-effect matrices are instrument design and electrical design at once | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.risk-analysis-fmea | HAZOP is driven node by node off the P&ID and quotes its tags throughout | §3.11 "One file may hold facts from more than one domain without losing information." |
| mro.asset-record | the equipment list and the asset register are the same equipment under two identifiers | §3.8 "The system must separate roles that happen to contain the same entity type." |
| hse.environmental-compliance | emission points are drawn on the P&ID and licensed on the permit | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.aerospace-airworthiness` — Aerospace type design and airworthiness data

The technical evidence that an aircraft, part or modification is approved to fly, and stays approved.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `aircraft_type` | string | A320 family | `validated` | the type the data applies to — the domain's top organising fact |
| `modification` | string | cabin reconfiguration mod 4471 | `validated` | the change being approved; the subject of a certification file |
| `approval_reference` | string | STC ST01234NY | `validated` | the approval's identity, corroborated by an authority token as under recognition |
| `authority` | string | EASA | `validated` | the certifying authority. §3.7 "It should use word-boundary matching rather than substring matching." matters here: three-letter authority names are inside many longer words |
| `certification_basis` | string | CS-25 amendment 27 | `validated` | the rule set the approval is against; a labeled field in the certification plan |
| `effectivity` | string | MSN 1200 onwards | `direct` | a labeled applicability or effectivity block; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `part_number` | string | HK2-4471-01 | `validated` | as elsewhere in this slice |
| `compliance_state` | string | complied with | `direct` | a labeled status field on a directive or bulletin record |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- an authority token ('EASA' | 'FAA' | 'CAA' | 'TCCA' | 'ANAC') matched on a word boundary, co-occurring with an approval-document term — 'type certificate' | 'supplemental type certificate' | 'authorised release certificate' | 'airworthiness directive' | 'service bulletin' | 'certification basis'
- an aircraft-type designation together with an effectivity block — 'applicability' | 'effectivity' | 'serial numbers affected' | 'MSN'
- a directive or bulletin numbering pattern together with a compliance-time statement ('compliance time' | 'before next flight' | 'at next scheduled maintenance')

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a stress or systems report that is certification evidence but names no approval reference
- deciding whether a manual excerpt is approved data or vendor information, which changes what may lawfully be done with it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an aircraft-type designation — 'A320' and '737' have the same shape as part numbers, room numbers and model names
- 'FAA' or 'EASA' inside a document that merely cites a rule, which most engineering procedures do
- a directive-style number

### Work types

`certification plan`, `compliance checklist`, `type-design data sheet`, `service bulletin`, `airworthiness directive`, `authorised release certificate`, `stress substantiation report`, `flight-test report`, `instructions for continued airworthiness`

### Grouping reasons (§4)

- one modification across its certification plan, substantiation and approval
- one aircraft type across the bulletins and directives that apply to it
- one approval reference across its issues — a §3.11 version family in which a superseded issue remains legally meaningful

### Template (§5)

`aircraft type → modification → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cert.certification-file | this is the aviation instance of product certification; the separating signal is a civil-aviation authority reference | §3.11 "One file may hold facts from more than one domain without losing information." |
| mro.maintenance-work-order | a service bulletin is design data and a work instruction at the same time, and the same document is filed in both places | §3.9 "The documents are content-incoherent but purpose-coherent." |
| eng.verification-validation | flight and ground test reports are certification evidence and test reports at once | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.requirements-specification | the certification basis is a requirement set imposed from outside | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

### Open question — for Joseph, unresolved

EXPORT-CONTROLLED TECHNICAL DATA is the operative restriction on this domain and the design has no concept for it. §8.4's corpus reaches identity, financial, medical, legal, credential, correspondence, GPS, employment and educational material and stops. A file that may not lawfully be shown to a foreign national, or transmitted outside a jurisdiction, is `none` under an honest reading of the design and may therefore take the cloud route. This is the sharpest instance of the slice-wide gap recorded on `eng.engineering-project`; Joseph decides whether P7 gains a category for it, or whether this domain is held off the model route by policy instead.

---

## `eng.automotive-program` — Automotive vehicle programme and homologation

A vehicle or automotive-component programme: its milestones, its customer requirements and its type approval.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `programme` | string | K2 facelift | `validated` | the programme identity; the automotive analogue of §3.11's project field |
| `vehicle_platform` | string | K-platform | `validated` | the platform the programme sits on |
| `customer_organisation` | string | the OEM | `validated` | §3.8 "The system must separate roles that happen to contain the same entity type." — for a supplier the OEM is the customer, and the same manufacturer may also be the vehicle's maker, an employer and a merely cited organisation. These are different roles of one entity type |
| `part_number` | string | HK2-4471-01 | `validated` | our part number. The customer's part number for the same item is a different field and frequently a different string, which is §3.8 "The system must separate roles that happen to contain the same entity type." inside one document |
| `milestone` | string | start of production | `validated` | the programme gate; the automotive vocabulary for `eng.stage-gate-review`'s gate |
| `regulation_reference` | string | UN R94 | `validated` | the type-approval regulation; corroborated as under recognition |
| `variant` | string | left-hand drive, export | `validated` | the build variant the document applies to |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- an automotive milestone token ('SOP' | 'PPAP' | 'run at rate' | 'DV' | 'PV' | 'gateway') together with a programme or platform name in a document title
- a UN/ECE or FMVSS regulation reference together with a vehicle-system term and a test or approval heading
- a customer-specific requirement reference (an OEM standard number) together with a supplier part number in the same title block or header row

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a supplier report whose OEM customer is identifiable only from a logo or letterhead
- deciding which of two part numbers in a document is ours and which is the customer's — §3.8 "The system must separate roles that happen to contain the same entity type."

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a vehicle model name — also a common product name and often an ordinary word
- a three-letter milestone token: 'DV', 'PV' and 'SOP' match a great deal else
- an OEM name on its own, for the role reason above

### Work types

`programme timing plan`, `DV/PV test plan`, `homologation dossier`, `customer-specific requirement matrix`, `production part approval submission`, `run-at-rate report`, `part submission warrant`, `field-quality report`

### Grouping reasons (§4)

- one programme across its milestones
- one part number across its design-validation, production-validation and approval evidence
- one variant across the approvals that cover it

### Template (§5)

`programme → milestone → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cert.certification-file | type approval is product certification under a sector-specific scheme | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.supplier-qualification | a production part approval submission is a programme artifact and a supplier-approval artifact at once | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.verification-validation | DV and PV testing is verification testing with a programme label on it | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.warranty-claim | field-quality reporting is a programme deliverable and a warranty analysis | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.material-specification` — Material and process specifications

An authored specification of a material, coating or special process — what it must be, and how that is verified.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `specification_number` | string | MS-2140 | `validated` | the specification's identity; corroborated by the control block, as in `eng.requirements-specification` |
| `category` | string | coatings | `validated` | metals, polymers, composites, coatings or special processes — the field that keeps the folder tree from becoming one directory per material |
| `material` | string | 6061-T6 aluminium | `validated` | the specified material; this domain's subject |
| `process` | string | hard anodise | `validated` | where the specification controls a process rather than a material |
| `revision` | string | D | `direct` | a labeled revision field; a position in a §3.11 version family |
| `verification_method` | string | coupon test per lot | `validated` | how conformance is proved, which is what separates a specification from a datasheet |
| `issuing_organisation` | string | Kestrel Dynamics | `validated` | recorded for search only. §3.8 "It should avoid using authorship or creator identity as a destination dimension." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a specification-number label ('specification no' | 'material spec' | 'process spec') together with a composition, property or process-parameter table (§2.3)
- a material designation pattern (an alloy, grade or polymer designation) co-occurring with a mechanical-property table header set — a tensile column beside a yield column beside an elongation column
- a process-parameter table (a bath, temperature, time or current-density column set) together with a specification number

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a material requirement stated only in a drawing note or a purchase description
- deciding whether a document specifies a material or merely reports a test on one — the property tables are identical

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an alloy or grade designation — '304', '6061' and 'PA66' match part numbers, room numbers and model numbers, and §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet"
- a property-table header set with no designation anywhere
- a process word such as 'anodise' or 'passivate'

### Work types

`material specification`, `process specification`, `coating or finish specification`, `welding procedure specification`, `heat-treatment specification`, `approved-source list`, `restricted-substance declaration`, `safety data sheet`

### Grouping reasons (§4)

- one specification across its issues
- one material across the specification, the certificates that evidence it and the parts that call it up

### Template (§5)

`category → material → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child" — the category level exists precisely because material-first would be a long flat list, and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.component-datasheet | an authored specification and a received datasheet contain the same property tables. §3.8 "The system must separate roles that happen to contain the same entity type." — our statement of what is required, versus the supplier's statement of what is supplied | §3.8 "The system must separate roles that happen to contain the same entity type." |
| cert.standards-library | a specification that is a national or industry standard we merely hold is a library item, not an authored one | §3.8 "The system must separate roles that happen to contain the same entity type." |
| qual.inspection-record | material certificates evidence the specification and are inspection records | §3.11 "One file may hold facts from more than one domain without losing information." |
| hse.environmental-compliance | restricted-substance declarations and safety data sheets are material documents and compliance documents | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.component-datasheet` — Component datasheets and vendor technical data

A vendor's technical statement about a part we buy — received material, never authored here.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." The role split it turns on is design-named: §3.8 "The system must separate roles that happen to contain the same entity type."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `manufacturer` | string | Analog Devices | `validated` | §3.8 "The system must separate roles that happen to contain the same entity type." — the manufacturer of a component, the supplier who sells it and our own organisation are three roles and must not collapse into one organisation field |
| `manufacturer_part_number` | string | LT8640SIV#PBF | `validated` | the part's identity in the vendor's namespace. It has the same shape as our own part numbers, so §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| `component_type` | string | step-down regulator | `validated` | what the part is; the first folder level, because a manufacturer-first tree is a collector |
| `datasheet_revision` | string | Rev C | `direct` | a labeled revision field on the document; a position in a §3.11 version family |
| `lifecycle_status` | string | not recommended for new designs | `validated` | the field that makes an old datasheet actionable rather than merely old |
| `package` | string | LQFN-32 | `validated` | the physical package; a search field and a selection field |
| `used_in_project` | string | Hawk Mk2 actuator | `llm_supported` | §3.13 "An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation." — the link from a received datasheet to our project is almost never stated in the datasheet and must come from the surrounding set |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a manufacturer name matched on a word boundary together with a manufacturer-part-number label ('part number' | 'order code' | 'ordering information') and a characteristics table (§2.3)
- an 'absolute maximum ratings' or 'recommended operating conditions' heading together with a package or pin-out figure caption — this header pair is close to universal in this document class and rare outside it

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned datasheet whose manufacturer appears only as a logo
- deciding whether a received PDF is a datasheet, a product manual or a marketing brochure: all three carry a manufacturer, a part number and a specification table

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a manufacturer part number — the same shape as our own part numbers, and §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet"
- a manufacturer name: §3.8 "The system must separate roles that happen to contain the same entity type.", and the same company appears as supplier, customer, employer and cited organisation
- a characteristics table

### Work types

`datasheet`, `application note`, `reference design`, `errata`, `product-change notification`, `end-of-life notice`, `declaration of conformity`, `safety data sheet`, `installation manual`

### Grouping reasons (§4)

- one manufacturer part number across its datasheet revisions
- one design across the datasheets of the parts it uses — a purpose group, not a content group
- one product-change notification across the parts it affects

### Template (§5)

`component type → manufacturer → artifact type`

Time first: **no**

manufacturer deliberately does not lead: §3.8 "A folder should not become a collection point for everything produced by the same person or organization." A directory per manufacturer is exactly that. Component type leads instead, which is also how anyone actually looks for a datasheet. §5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| admin.warranties | a component datasheet and a purchased-product manual are one document class seen from two lives — filed by an engineer against a design, or by a householder against a purchase. The document itself does not distinguish them; the deciding evidence is external, a part number that appears in a BOM or schematic on one side, a receipt, warranty or inventory row on the other | §3.11 "One file may hold facts from more than one domain without losing information." |
| pers.household-inventory | the same file, filed as a possession rather than as a component | §3.9 "The documents are content-incoherent but purpose-coherent." |
| cert.standards-library | both are received reference documents held rather than authored | §3.8 "The system must separate roles that happen to contain the same entity type." |
| eng.material-specification | the authored specification and the received datasheet, above | §3.8 "The system must separate roles that happen to contain the same entity type." |
| soft.hardware-design-file | the software slice already names 'datasheet' among its work types | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.risk-analysis-fmea` — Design and process risk analysis

Structured analysis of how a design or a process can fail, before it has — FMEA, HAZOP, fault tree, hazard log.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Hawk Mk2 actuator | `validated` | §3.11's project field |
| `analysed_item` | string | front housing seal | `validated` | the item, function or node being analysed |
| `analysis_method` | string | DFMEA | `validated` | DFMEA, PFMEA, HAZOP, FMECA or fault tree — genuinely different methods with different table shapes |
| `function_or_node` | string | node 4, feed line | `validated` | the analysis unit; a HAZOP works node by node and an FMEA function by function |
| `revision` | string | 3 | `direct` | a labeled revision field; a position in a §3.11 version family, since a living FMEA supersedes rather than accumulates |
| `risk_rating` | string | high | `validated` | the qualitative band only. §3.13 "The product may calculate internal numeric scores to rank competing candidates, but the stored record must preserve the kind and quality of evidence behind the conclusion." |
| `status` | string | actions open | `direct` | a labeled status field |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a method token ('FMEA' | 'DFMEA' | 'PFMEA' | 'HAZOP' | 'FMECA' | 'fault tree') in a title together with an analysis-table header cluster — a failure-mode column beside an effect column beside a cause column
- a HAZOP guideword set ('no' | 'more' | 'less' | 'reverse' | 'as well as') appearing as a column or row set together with a node or line reference
- a hazard-log table pairing a hazard-reference column with a control column and a residual-risk column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a risk discussion recorded in minutes that is an FMEA in substance and not in form
- deciding whether a hazard log belongs to design risk, workplace safety or programme risk — all three use the word

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'risk' — this slice uses it for design risk, programme risk, financial risk and workplace risk
- a severity or likelihood column with no failure-mode column: audit reports have the same pair
- 'FMEA' inside a procedure that merely requires one to exist

### Work types

`design FMEA`, `process FMEA`, `HAZOP worksheet`, `fault tree`, `hazard log`, `risk assessment`, `control plan`, `mitigation action list`

### Grouping reasons (§4)

- one analysed item across its analysis revisions
- one node or function across analysis, mitigation and the verification that closed it
- one method campaign across the sessions that made it up

### Template (§5)

`project → analysed item → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| hse.safety-case | the safety case argues from these analyses and reproduces their tables | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.failure-analysis-rca | the same vocabulary pointing in opposite directions in time: failure modes predicted here, failure modes observed there. A document that contains both is common and belongs to both | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.process-flow-pid | a HAZOP is inseparable from the P&ID it walks | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.nonconformance-capa | the control plan links analysis to the controls a nonconformance later tests | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.prototype-build` — Prototype builds, additive manufacturing and build records

A physical build of a design at a point in time — prototype units, print jobs, and the record of what was actually made.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Hawk Mk2 actuator | `validated` | §3.11's project field |
| `build_identifier` | string | EVT-3 unit 07 | `validated` | the build's identity — the field that makes one build distinguishable from the next |
| `build_stage` | string | EVT | `validated` | engineering, design or production validation; a labeled or headed field |
| `part_number` | string | HK2-4471-01 | `validated` | as elsewhere in this slice |
| `process` | string | selective laser sintering | `validated` | the making process — additive, machined, moulded or hand-built |
| `material` | string | PA12 | `validated` | the material actually used, which is often not the material specified |
| `machine` | string | EOS P396, cell 2 | `direct` | a labeled machine or job field in a build report or machine log |
| `build_date` | string | 2026-04-02 | `direct` | a labeled date field; §3.10 "Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a build-stage token ('EVT' | 'DVT' | 'PVT' | 'prototype build' | 'mule' | 'alpha build') together with a project or part-number token in a document title or a §2.9 spreadsheet sheet name
- an additive artifact set: a slicer or build-file extension together with a build report or machine log naming the same job name and a material
- a build-log table whose headers pair a unit or serial column with a build-date column and an issue or observation column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- photographs of a build with no accompanying written record
- deciding whether a print job is a work build or a personal print — the model, the slicer output and the machine log are identical in both lives

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an STL, 3MF or G-code extension — the clearest over-firing pattern in this domain, and §2.9 "unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty" leaves nothing inside the file to disambiguate it
- a machine name
- a three-letter build-stage token

### Work types

`build plan`, `build log`, `prototype unit record`, `slicer or build file`, `machine log`, `build review notes`, `rework record`, `teardown report`, `print-farm job sheet`

### Grouping reasons (§4)

- one build across its plan, units, logs and review
- one project across its successive build stages
- one printed part across its model, slicer file and machine log — a derived set, not a version family

### Template (§5)

`project → build stage → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.hobby-collection | a personal 3D print produces this exact file set with the same tools and the same names, and nothing inside any of the files decides which life it belongs to | §2.9 "unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty" |
| pers.creative-project | a maker project is a prototype build without an organisation behind it | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.cad-model | the build consumes the model, and the two are frequently in one folder | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.verification-validation | the build produces the units the tests consume, and the unit serials appear in both records | §3.11 "One file may hold facts from more than one domain without losing information." |
| mfg.production-record | the last prototype units and the first production units are the same shape of record | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.verification-validation` — Test plans, protocols and validation reports

Planned testing against a stated requirement, and the report that says whether it passed.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Hawk Mk2 actuator | `validated` | §3.11's project field |
| `tested_item` | string | front housing assembly | `validated` | the article under test; this domain's subject |
| `test_identifier` | string | TP-4471-03 | `validated` | the plan or report identity, corroborated by the document-control block |
| `requirement_reference` | string | SPEC-HK2-014 REQ-021 | `validated` | what the test closes. This is the field that distinguishes an engineering test report from a research result, and it is the one most often absent |
| `test_standard` | string | IEC 60068-2-1 | `validated` | the method standard; corroborated, because a standard number alone is worthless |
| `result` | string | pass | `direct` | a labeled result or verdict field; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `test_date` | string | 2026-05-14 | `direct` | a labeled date field |
| `facility` | string | environmental lab 2 | `validated` | where the test ran; a search field, and evidence about independence |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a test-document label ('test plan' | 'test procedure' | 'test report' | 'validation report' | 'qualification report') in a title together with a tested-item identifier and a result or acceptance-criteria block
- a requirement-to-test cross-reference table (§2.3) pairing a requirement-identifier column with a test-identifier column and a result column — the strongest signal in this domain and the one that separates it from research output
- a test-standard reference together with a specimen or sample identifier in a table header

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a report of an experiment that never states which requirement it closes
- distinguishing a qualification test from a research experiment when both use the same rig, the same standard and the same instrument output

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- 'pass' or 'fail' — the words appear in every checklist in this slice
- a standard number: §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.", and a standard number has the same shape as all of it
- a specimen identifier

### Work types

`test plan`, `test procedure`, `test report`, `validation report`, `qualification report`, `raw data record`, `deviation from procedure`, `correlation report`, `test-rig calibration statement`

### Grouping reasons (§4)

- one tested item across its plan, procedure, data and report
- one requirement across the tests that close it — a purpose group, since the documents are content-diverse
- one test report across its issues: a re-issued report supersedes rather than adds, so this is a §3.11 version family

### Template (§5)

`project → tested item → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.instrument-output | the artifact is identical: an instrument produced data and a person wrote it up. §3.9 "The documents are content-incoherent but purpose-coherent." decides it — this report exists to close a requirement, the research artifact exists to answer a question — and neither purpose is readable from the data file. Both are readable from the surrounding set: a requirement cross-reference on one side, a manuscript or a venue on the other | §3.9 "The documents are content-incoherent but purpose-coherent." |
| res.protocol-sop | a test protocol and a laboratory protocol are the same document class | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.inspection-record | inspection measures conformance of a produced item; verification measures conformance of a design | §3.8 "The system must separate roles that happen to contain the same entity type." |
| cert.certification-file | a test report submitted as certification evidence is fully both | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.simulation-fea | the correlation report belongs to the test and to the analysis | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.commissioning-handover` — Commissioning and handover packages

The evidence pack that transfers a completed installation from the people who built it to the people who will run it.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." Structurally it is §3.9 "The documents are content-incoherent but purpose-coherent."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Unit 400 debottleneck | `validated` | §3.11's project field |
| `system` | string | feed pump skid | `validated` | the system being handed over; this domain's subject |
| `site` | string | Teesside | `validated` | the physical location |
| `commissioning_stage` | string | pre-commissioning | `validated` | factory acceptance, pre-commissioning, cold or hot commissioning — genuinely sequential states |
| `completion_reference` | string | punch item A-214 | `validated` | the outstanding-work identity, which is what makes a punch list navigable |
| `handover_date` | string | 2026-06-30 | `direct` | a labeled date on the taking-over certificate |
| `witness_role` | string | client representative | `direct` | the role that signed, not the individual: §3.8 "It should avoid using authorship or creator identity as a destination dimension." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a commissioning vocabulary cluster — two or more of 'pre-commissioning' | 'cold commissioning' | 'site acceptance test' | 'factory acceptance test' | 'punch list' | 'snagging' | 'taking over certificate' | 'practical completion' — together with a system or site name
- a check-sheet set whose §2.3 table pairs a witnessed-by signature column with a date column, together with an equipment tag or system name
- a handover index: a document-number column beside a document-title column beside a status column, under a handover or turnover heading

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a handover sent as an email with the pack as attachments and no cover document
- deciding whether a document is the commissioning record or the operating manual it references

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- 'SAT' and 'FAT' — three-letter tokens matching a great deal else
- a signature column: every inspection, calibration and production record in this slice has one
- a site name

### Work types

`commissioning plan`, `factory or site acceptance record`, `pre-commissioning check sheet`, `punch or snag list`, `taking-over certificate`, `handover index`, `training record`, `operating and maintenance manual index`

### Grouping reasons (§4)

- one system across its check sheets and certificate
- one handover across the index and every document the index lists — a purpose group whose members are content-diverse
- one punch item from raising to close-out

### Template (§5)

`project → site → system → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.as-built-record | the handover pack contains the as-builts; the pack is a purpose and the as-built an artifact | §3.9 "The documents are content-incoherent but purpose-coherent." |
| mro.asset-record | handover is where an asset record is born, and the nameplate data comes straight out of the pack | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.inspection-record | acceptance test sheets are inspection records under another name | §3.11 "One file may hold facts from more than one domain without losing information." |
| mfg.work-instruction | operating and maintenance manuals are operating instructions and handover deliverables at once | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.as-built-record` — As-built and record documentation

What was actually installed, as opposed to what was drawn — the record of reality after construction or modification.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Bramley Street footbridge | `validated` | §3.11's project field |
| `asset` | string | north abutment | `validated` | the built thing the record describes |
| `drawing_number` | string | BSF-S-1204 | `validated` | the design drawing this records against; as in `eng.drawing-package` |
| `as_built_revision` | string | AB01 | `direct` | a labeled revision or status field. Whether this is another member of the design drawing's §3.11 version family or the first member of a separate one is an organisational convention, not a fact in the file |
| `survey_date` | string | 2026-07-08 | `direct` | a labeled survey or record date |
| `site` | string | Bramley Street | `validated` | the physical location |
| `discipline` | string | structural | `validated` | as elsewhere in this slice |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- an as-built marking ('as built' | 'as installed' | 'record drawing' | 'as constructed') in a title block or a stamped annotation, together with a drawing number
- a red-line markup layer on a drawing file whose stem matches a released drawing — §2.9 promises "layers or artboards where accessible" for these formats, which is exactly the evidence needed
- a dimensional-survey table pairing a designed-value column with an as-constructed column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographic survey used as the as-built record with no drawing at all
- deciding whether an annotated drawing is an as-built record or a design markup that was never built

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the phrase 'as built' inside a specification that merely requires as-builts — every construction specification does
- a red annotation
- a drawing number

### Work types

`as-built drawing`, `record drawing`, `red-line markup`, `dimensional survey`, `point cloud or scan`, `as-built bill of materials`, `modification record`, `survey report`

### Grouping reasons (§4)

- one asset across its as-built set
- one drawing number across design issue and as-built issue — one §3.11 version family or two, and organisations genuinely disagree
- one modification across the drawings it changed

### Template (§5)

`project → asset → discipline → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.drawing-package | the as-built and the design drawing share a number, and often a file | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.commissioning-handover | as-builts are the largest single component of a handover pack | §3.9 "The documents are content-incoherent but purpose-coherent." |
| mro.asset-record | the as-built is the asset's founding document | §3.11 "One file may hold facts from more than one domain without losing information." |
| pers.home-tenure | a householder's as-builts of their own property are a property record too | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `eng.invention-disclosure` — Invention disclosures and technical patent material

The technical description of an invention around the moment of filing — the engineer's half of a patent.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Hawk Mk2 actuator | `validated` | §3.11's project field; most disclosures arise out of a project |
| `disclosure_reference` | string | IDF-2026-014 | `validated` | the internal identity of the disclosure |
| `invention_title` | string | compliant seal retention feature | `direct` | a labeled title field on the disclosure form; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `technology_area` | string | sealing systems | `validated` | the subject grouping; the first folder level |
| `filing_reference` | string | US 18/123,456 | `validated` | the application or publication number, corroborated by an office token |
| `status` | string | filed, awaiting examination | `validated` | disclosed, filed, published, granted, abandoned — a labeled status field |
| `priority_date` | string | 2026-02-10 | `direct` | a labeled date field; it is the fact everything else in a patent hangs on |
| `inventor_names` | list of strings | recorded, never a folder level | `direct` | §3.8 "It should avoid using authorship or creator identity as a destination dimension." Inventorship is a legal fact and must be stored, but it is metadata here and never a dimension |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a disclosure-form field set: an invention-title field together with an inventors field and at least one of 'first disclosure' | 'prior art' | 'enablement' | 'best mode' | 'date of conception'
- an application or publication number pattern together with a patent-office token and a filing-status word
- a claim-set structure — a numbered claim block whose first claim is independent and whose later claims recite 'according to claim' — together with a figure list

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a technical note that is an invention disclosure in substance with no form around it
- deciding whether a document is the engineer's technical disclosure or the attorney-drafted specification

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an application-number-shaped code
- the word 'patent' inside a document that merely cites one, which many datasheets and specifications do
- an inventor name — for the §3.8 reason above, and because the same person authors most of this slice

### Work types

`invention disclosure form`, `prior-art search`, `draft specification`, `patent figures`, `inventor declaration`, `filing receipt`, `office-action technical response`, `defensive publication`, `freedom-to-operate note`

### Grouping reasons (§4)

- one invention across its disclosure, search, figures and filing
- one patent family across its filings in different offices — a family in the ordinary patent sense, which is not a §3.11 version family: the members are distinct legal instruments, not states of one document

### Template (§5)

`technology area → invention → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.patent-disclosure | the research slice holds the same object seen from the laboratory; a disclosure arising from research is genuinely both | §3.11 "One file may hold facts from more than one domain without losing information." |
| law.ip-prosecution | the attorney's matter file holds the same documents under a matter number rather than a project | §3.8 "The system must separate roles that happen to contain the same entity type." |
| legal.ip-registration | the registration record is the administrative half of the same filing | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.requirements-specification | a draft specification and a patent specification share the word and nothing else, which is a real retrieval hazard | §3.8 "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase §2.9 "potentially sensitive" is the only marking made here. The hook is §8.4's own list: a disclosure becomes a filing and a filing is a legal record, and the document carries named inventors and an assignment position. State the limit honestly, though — the reason engineers guard a disclosure is that publication before filing destroys novelty, and §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." names no such thing. That gap is recorded as the open question on `eng.engineering-project`. The handling CLASS is P7's (§8.4) and is not set.

---

## `cert.certification-file` — Product certification and conformity files

The file that shows a product meets a regulation or a standard, and the certificate that comes out of it.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `product` | string | Hawk Mk2 actuator | `validated` | the certified thing; this domain's subject |
| `certification_scheme` | string | UKCA | `validated` | the scheme or marking regime — the field that decides which evidence is required |
| `standard_reference` | string | EN 60335-1 | `validated` | the standard complied with, corroborated as under recognition |
| `certificate_number` | string | TUV-R-50412345 | `validated` | the certificate's identity |
| `certification_body` | string | a notified body | `validated` | §3.8 "The system must separate roles that happen to contain the same entity type." — the certification body, the manufacturer and the test laboratory are three roles and often three organisations |
| `issue_date` | string | 2026-01-19 | `direct` | a labeled date on the certificate |
| `expiry_date` | string | 2031-01-18 | `direct` | a labeled expiry or valid-until field; the field that makes a certificate actionable |
| `scope` | string | models HK2-A through HK2-D | `llm_supported` | §3.13 "An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation." — the scope clause is prose and its boundaries frequently need interpretation |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a certificate layout: a certificate-number label together with an issuing-body name matched on a word boundary and a standard reference inside a scope block
- a declaration-of-conformity heading together with a directive or regulation citation and a manufacturer block
- a technical-file index whose §2.3 table lists standards in one column against evidence documents in another

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned certificate whose issuing body appears only as a logo
- deciding whether a certificate certifies the product, the factory or a person — the three read almost identically

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a standard number — the most over-firing token in this domain. Standard numbers appear in specifications, drawings, test reports, purchase orders and marketing sheets alike, and §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet"
- a certificate number
- the word 'certificate'

### Work types

`declaration of conformity`, `type-examination certificate`, `notified-body test report`, `technical file index`, `certification risk assessment`, `user instructions as evidence`, `surveillance audit report`, `marking artwork`

### Grouping reasons (§4)

- one product across its scheme, standards and evidence — a purpose group whose members are content-diverse
- one certificate across its renewals, which is a §3.11 version family of issues of one instrument

### Template (§5)

`product → certification scheme → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.professional-license | a person's certification and a product's certification are one word and two different objects; §3.8 "The system must separate roles that happen to contain the same entity type." is the rule that keeps them apart, and the corpus will contain both | §3.8 "The system must separate roles that happen to contain the same entity type." |
| cert.standards-library | the standard we comply with, versus the standard we merely hold on the shelf | §3.8 "The system must separate roles that happen to contain the same entity type." |
| eng.verification-validation | the test reports inside the file are test reports in their own right | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.management-system | a management-system certificate certifies the system, not the product, and the two certificates look identical | §3.8 "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `cert.standards-library` — Standards and codes reference library

Standards, codes and regulations held as reference — received documents, usually licensed, never authored here.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." Its nearest design analogue is a residual reading collection: §7.3 "Reading Inbox may hold papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `standard_number` | string | ISO 2768-1 | `validated` | the document's identity, corroborated as under recognition |
| `issuing_body` | string | ISO | `validated` | the standards body; part of the identity, because a national adoption of one standard is a different document |
| `edition_year` | string | 2015 | `direct` | a labeled edition or publication field; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `title` | string | General tolerances | `direct` | the document title; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `status` | string | withdrawn | `validated` | current, superseded or withdrawn — and a superseded edition is still a distinct legal object, not a stale copy |
| `subject_area` | string | dimensional metrology | `validated` | the grouping that makes a standards library navigable; the first folder level |
| `licence_state` | string | single-user licence | `llm_supported` | §3.13 "An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation." — the licence terms are prose in the front matter and rarely a labeled field. See this entry's open question |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a standards-body prefix matched on a word boundary ('ISO' | 'EN' | 'ASTM' | 'IEC' | 'DIN' | 'JIS' | 'ASME' | 'BS') immediately followed by a number pattern, together with the heading set almost every standard shares — 'scope' AND 'normative references' AND 'terms and definitions'
- a copyright or licensing block naming a standards body together with an edition or publication-date field

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an extract or excerpt of a standard with the front matter removed
- deciding whether a held document is the standard itself or our own procedure that implements it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a standards-body prefix alone: 'EN' is a language token and a substring of ordinary words, which is exactly why §3.7 "It should use word-boundary matching rather than substring matching."
- a number following a prefix
- the word 'standard' — this slice uses it for standard work, standard parts and standard operating procedures

### Work types

`standard`, `code of practice`, `regulation or directive text`, `amendment or corrigendum`, `national annex`, `interpretation or guidance`, `standards-watch list`, `purchased extract`

### Grouping reasons (§4)

- one standard across its editions and amendments — a §3.11 version family whose superseded members remain legally meaningful
- one subject area across the standards that govern it

### Template (§5)

`subject area → issuing body`

Time first: **no**

the standard number is the filename, not a folder: one directory per standard is §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." Subject area leads because that is how a standard is looked for, and §5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.reference-library | a held paper and a held standard are both received reading with no project of their own | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.material-specification | a national material standard and an internal material specification are the same document shape | §3.8 "The system must separate roles that happen to contain the same entity type." |
| eng.requirements-specification | a specification that is mostly call-ups looks like a standard | §3.8 "The system must separate roles that happen to contain the same entity type." |
| cert.certification-file | the standard complied with sits inside the certification file as evidence | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

### Open question — for Joseph, unresolved

LICENSED THIRD-PARTY MATERIAL. This is the one class of file in this slice whose restriction is contractual rather than personal. A single-user licence for a standard commonly forbids copying and redistribution, and sending the full text to a cloud model is at least arguably both. §8.4 governs personal sensitivity — §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — and has no concept of a third-party licence, so nothing in the design stops the model route here and this catalogue does not invent a stop. Joseph decides whether P7 gains a category for licensed third-party material, or whether it is handled by policy outside the catalogue.

---

## `mfg.production-planning` — Production planning and scheduling

What will be made, in what quantity, on which line, and when.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." Its recognition depends on the design-named spreadsheet path: §2.9 "Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site` | string | Teesside plant | `validated` | the making location; a folder level only where a corpus spans sites |
| `product` | string | Hawk Mk2 | `validated` | what is being planned; this domain's subject |
| `plan_type` | string | master production schedule | `validated` | MPS, MRP output, finite schedule or capacity plan — genuinely different documents |
| `plan_horizon` | string | week 34 to week 40 | `direct` | a labeled period field in the header |
| `work_centre` | string | assembly cell 2 | `validated` | the line or cell the plan loads |
| `order_reference` | string | WO-88412 | `validated` | the released order identity; the same number range as maintenance work orders, which is the collision below |
| `planning_system` | string | ERP export | `direct` | recorded because it changes how the file should be read; §2.2 "PDF metadata should be treated as supporting evidence, not as truth." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a §2.9 spreadsheet whose sheet name or header row carries a planning term ('MPS' | 'MRP' | 'production plan' | 'production schedule') together with a part-number column and a due-date column
- a work-order-number label together with a quantity column and a work-centre or line identifier
- a capacity table pairing a work-centre column with an available-capacity column and a load column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a plan communicated as a table pasted into an email
- deciding whether a schedule is production, project or shift roster — the grid looks the same

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a date column
- a quantity column
- a work-order-shaped number: it matches invoice numbers, job numbers and maintenance orders throughout this catalogue

### Work types

`master production schedule`, `MRP output`, `work order`, `production schedule`, `capacity plan`, `changeover plan`, `shortage or expedite list`, `line-balance sheet`

### Grouping reasons (§4)

- one planning period across its plan, released orders and shortages
- one product across its planned and released orders

### Template (§5)

`site → product → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child" §5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| mfg.production-record | plan and actual are two documents about one intention, and often two tabs of one file | §3.11 "One file may hold facts from more than one domain without losing information." |
| mro.maintenance-work-order | both are work orders, the number ranges frequently overlap, and neither document says which system issued it | §3.8 "The system must separate roles that happen to contain the same entity type." |
| biz.procurement-po | the purchase orders that feed the plan carry the same part numbers and dates | §3.8 "The system must separate roles that happen to contain the same entity type." |
| mro.spare-parts | shortage lists and stock reports are the same table with a different owner | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `mfg.work-instruction` — Work instructions and manufacturing SOPs

The controlled instruction that tells an operator exactly how to perform one operation.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `document_number` | string | WI-A2-014 | `validated` | the controlled identity, corroborated by the control block |
| `revision` | string | 6 | `direct` | a labeled revision field. Its meaning here is unusually sharp: only the current issue may be at the workstation, so the §3.11 version family has exactly one live member and the rest are retained history |
| `product` | string | Hawk Mk2 | `validated` | what is being made |
| `operation` | string | final assembly, station 4 | `validated` | the operation the instruction covers; this domain's subject |
| `work_centre` | string | assembly cell 2 | `validated` | where it is performed |
| `instruction_type` | string | assembly | `validated` | assembly, setup, inspection, packing or changeover |
| `approval_state` | string | released | `direct` | a labeled approval or effective-date field; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a controlled-document header — a document-number label together with a revision label and an approval or effective-date field — co-occurring with an instruction vocabulary cluster: numbered steps used as headings together with 'tools required' | 'personal protective equipment' | 'caution' | 'operation no'
- an operation-number field together with a work-centre field in a §2.3 table header
- a setup sheet pairing a parameter column with a setting column, under a part number and a machine

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photo-led instruction with almost no extractable text — a common and genuinely hard case, since §2.6 "Images require their own extraction pipeline because filenames often carry little semantic meaning."
- distinguishing a work instruction from a maintenance procedure or a consumer manual: all three share the step-and-caution shape exactly

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- numbered steps — every procedure, recipe, manual and protocol in this catalogue has them
- the word 'procedure'
- a document number

### Work types

`work instruction`, `standard operating procedure`, `setup sheet`, `inspection instruction`, `packing instruction`, `changeover instruction`, `visual aid`, `one-point lesson`

### Grouping reasons (§4)

- one instruction across its revisions — a §3.11 version family in which exactly one member is live
- one product across the instructions of its routing, in operation order

### Template (§5)

`product → operation → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| mro.maintenance-work-order | maintenance procedures have this shape precisely and often this numbering | §3.8 "The system must separate roles that happen to contain the same entity type." |
| qual.management-system | a system procedure and a shop-floor instruction are one document class at two altitudes | §3.11 "One file may hold facts from more than one domain without losing information." |
| soft.runbook-operational-doc | the software slice's runbook is this document written for a system rather than a machine | §3.11 "One file may hold facts from more than one domain without losing information." |
| career.continuing-education | the operator competency and training records that accompany an instruction are employment records and belong to the career slice, not here — that split is why this entry is not marked sensitive | §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `mfg.production-record` — Production and batch records

What was actually made: the traveller, route card or batch record that follows a job through the shop.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `product` | string | Hawk Mk2 | `validated` | what was made |
| `part_number` | string | HK2-4471-01 | `validated` | as elsewhere in this slice |
| `order_reference` | string | WO-88412 | `validated` | the job identity that ties every sheet in the record together |
| `batch_or_lot` | string | L-2026-0412 | `validated` | the lot identity, which is what makes a recall traceable |
| `serial_range` | string | 0118 to 0164 | `direct` | a labeled serial or from-to field |
| `disposition` | string | accepted | `direct` | a labeled disposition field; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `production_date` | string | 2026-04-22 | `direct` | a labeled date field |
| `operation_sequence` | string | op 010 to op 090 | `direct` | the routing steps recorded on the card |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a traveller header: a work-order label together with a part-number label and an operation-sequence table whose rows carry a sign-off or date column
- a batch or lot label together with a part number and a disposition field whose values are the material vocabulary — 'accepted' | 'quarantine' | 'scrap' | 'rework'
- a serial-number column beside a build-date column in a §2.9 spreadsheet whose sheet name carries a production term

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned, hand-completed route card, which is the normal case in older shops
- deciding whether a record is production, inspection or maintenance when all three carry a job number, a date and a sign-off

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a sign-off column
- a lot-number-shaped token
- a job number — the shared number space with `mfg.production-planning` and `mro.maintenance-work-order` is real and the document usually does not say which system issued it

### Work types

`traveller or route card`, `batch record`, `device history record`, `serial or build list`, `scrap and rework record`, `downtime log`, `shift handover log`, `label and marking record`

### Grouping reasons (§4)

- one work order across its operations and sign-offs
- one lot across its record, inspection results and disposition
- one serial number across everything ever recorded against it — the group that matters most and the one hardest to assemble

### Template (§5)

`product → artifact type`

Time first: **no**

one folder per work order is §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." §5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| qual.inspection-record | inspection results are stapled into the traveller and exist as records in their own right | §3.11 "One file may hold facts from more than one domain without losing information." |
| mfg.production-planning | plan and actual | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.nonconformance-capa | a scrap or rework record is a production record and a nonconformance at once | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.prototype-build | the last prototype units and the first production units are the same record shape | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `mfg.tooling-fixture` — Tooling, moulds and fixtures

The things that make the things — moulds, dies, jigs, fixtures and gauges, each an asset with a life of its own.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `tool_number` | string | T-2201 | `validated` | the tool's identity. §3.8 "The system must separate roles that happen to contain the same entity type." applies inside this one domain: the tool number and the number of the part it makes are two roles of one entity type and are routinely confused |
| `tool_type` | string | injection mould | `validated` | mould, die, jig, fixture, gauge or check aid; the first folder level |
| `produced_part_number` | string | HK2-4471-01 | `validated` | what the tool makes — the pairing that corroborates the tool number |
| `tool_owner` | string | customer-owned | `validated` | §3.8 "The system must separate roles that happen to contain the same entity type." — a tool owned by us and held at a supplier, or owned by a customer and held by us, is the normal case and the ownership is a different fact from the location |
| `location` | string | supplier site, Wuxi | `validated` | where the tool physically is |
| `cavity_or_station` | string | 4 cavity | `direct` | a labeled field on the tool drawing or trial report |
| `maintenance_state` | string | due for refurbishment | `validated` | the field that turns a tool record into an actionable one |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a tool-number label ('tool no' | 'mould no' | 'fixture no' | 'gauge no' | 'die no') together with a produced-part reference — the pairing of two different part numbers in defined roles is the corroboration
- a drawing whose title block carries a tool-type token together with a cavity or station annotation
- a tool-trial report pairing a shot or cycle column with a dimensional-result column, under a tool number

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a tool referred to only by a shop nickname, which is the usual case on the floor
- deciding whether a drawing is of the part or of the fixture that holds it — they are drawn in the same style with the same title block

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a tool-number-shaped token
- the word 'fixture' — also a plumbing term, a sports term and a software-testing term
- a part number, for the role reason above

### Work types

`tool drawing`, `tool specification`, `tool trial report`, `tool maintenance record`, `tool ownership or transfer agreement`, `gauge study`, `cavity map`, `spare insert list`

### Grouping reasons (§4)

- one tool across its drawing, trials and maintenance history
- one produced part across the tools that make it
- one tool transfer across the agreement, the shipping record and the requalification

### Template (§5)

`tool type → artifact type`

Time first: **no**

the tool number is a fact and a filename; one directory per tool is §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." Where a corpus holds many documents per tool the user can add the tool level, which is §5.8 "The product should not force every branch to use the full template or have the same number of levels."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| mro.asset-record | a tool is a capital asset with a register entry, and both records claim the same nameplate | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.drawing-package | a tool drawing is a drawing with a title block, and the drawing register does not distinguish them | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.calibration-record | gauges are tools and calibrated items simultaneously, under one number | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.supplier-qualification | tools we own and a supplier holds appear in both files, and §3.8 "The system must separate roles that happen to contain the same entity type." | §3.8 "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `qual.management-system` — Quality management system documentation

The documented quality system itself — manual, procedures, audits and management reviews.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `standard_reference` | string | ISO 9001:2015 | `validated` | the management-system standard the system runs to |
| `process_area` | string | purchasing | `validated` | the process the document governs; the first folder level |
| `document_number` | string | QP-07 | `validated` | the controlled identity |
| `revision` | string | 4 | `direct` | a labeled revision field; a §3.11 version family with one live member, as with work instructions |
| `audit_type` | string | internal | `validated` | internal, customer, certification-body or supplier — four different documents in one template |
| `scope_site` | string | Teesside plant | `validated` | the certified or audited scope |
| `certification_status` | string | certified, next surveillance due | `validated` | the state of the system, as distinct from the state of any document in it |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a management-system standard reference together with a decimal clause structure in headings and a quality vocabulary cluster — 'quality manual' | 'management review' | 'internal audit' | 'nonconformity' | 'corrective action'
- an audit-report header set: an audit-scope field together with auditor and auditee fields and a finding table (§2.3)
- a document-control register: a document-number column beside a title column beside a revision column beside an owner column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a procedure that is part of the system but never cites the standard
- deciding whether a finding belongs to the quality, environmental or safety system when one audit template serves all three

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- 'ISO 9001' inside a document that merely claims compliance — every supplier brochure does
- the word 'quality'
- a clause number

### Work types

`quality manual`, `system procedure`, `internal audit plan`, `audit report`, `finding record`, `management review minutes`, `quality objectives`, `certification-body report`, `document-control register`

### Grouping reasons (§4)

- one audit across its plan, report and findings
- one procedure across its revisions
- one certification cycle across its surveillance audits

### Template (§5)

`process area → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child" §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cert.certification-file | the system certificate and the product certificate are the same object shape and different scopes | §3.8 "The system must separate roles that happen to contain the same entity type." |
| qual.nonconformance-capa | audit findings become corrective actions and the two records overlap completely | §3.11 "One file may hold facts from more than one domain without losing information." |
| corp.compliance-audit | the finance slice's general compliance-audit entry has this document shape exactly; the separating signal is whether the audited object is a management system or a financial control | §3.8 "The system must separate roles that happen to contain the same entity type." |
| mfg.work-instruction | the system procedure and the shop instruction, above | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `qual.inspection-record` — Inspection and measurement records

Measured evidence that a produced item conforms — dimensional, visual, functional and material.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `product` | string | Hawk Mk2 | `validated` | the product the inspected part belongs to; the first folder level |
| `part_number` | string | HK2-4471-01 | `validated` | the inspected item |
| `drawing_revision` | string | C | `direct` | the revision inspected against, read from a labeled field. This is the single most consequential field in the domain: a report measured against a superseded revision proves nothing, and it is a member reference into the drawing's §3.11 version family |
| `inspection_type` | string | first article | `validated` | first article, incoming, in-process, final or source — different documents with one table shape |
| `characteristic_reference` | string | balloon 12 | `validated` | which drawing characteristic the row measures |
| `result_disposition` | string | accept | `direct` | a labeled result field; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `lot_or_serial` | string | L-2026-0412 | `validated` | what was inspected, tying the record to `mfg.production-record` |
| `equipment_used` | string | CMM 3 | `validated` | the measuring equipment, which links to its calibration record |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a dimensional-report table whose headers pair a characteristic or balloon column with a nominal column and an actual or measured column. The nominal-and-actual pairing is what makes it an inspection record rather than any other table of measurements
- an inspection-type label ('first article' | 'incoming inspection' | 'in-process inspection' | 'final inspection' | 'CMM report') together with a part number and a drawing revision
- a measuring-machine output whose header block names a part and a program, together with a tolerance column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photograph of a completed paper inspection sheet that OCRs poorly
- deciding whether a measurement set is inspection, calibration or test — the tables are near identical and only the measured object differs

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a nominal-and-actual column pair with no part number: a calibration certificate has the same pair
- 'FAI' — a three-letter token
- a measured value

### Work types

`first article inspection report`, `dimensional report`, `CMM report`, `incoming inspection record`, `in-process check sheet`, `final inspection record`, `material certificate`, `certificate of conformity`, `visual inspection record`

### Grouping reasons (§4)

- one part number across its inspection history
- one lot across its incoming, in-process and final records
- one first-article submission across its report, the ballooned print and the drawing revision it was measured against

### Template (§5)

`product → inspection type → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| qual.calibration-record | the same measurement shape: calibration measures the instrument, inspection measures the part | §3.8 "The system must separate roles that happen to contain the same entity type." |
| eng.verification-validation | verification proves the design, inspection proves the item, and a first article does both | §3.9 "The documents are content-incoherent but purpose-coherent." |
| mfg.production-record | inspection sheets live inside the traveller | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.supplier-qualification | supplier first articles and part-approval submissions are inspection records and approval records at once | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.gdt-tolerance | the measured result closes the predicted stack | §3.9 "The documents are content-incoherent but purpose-coherent." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `qual.calibration-record` — Calibration and metrology records

Proof that a measuring instrument was, at a stated moment, traceable and within tolerance.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `instrument_identifier` | string | MIC-0412 | `validated` | the instrument's identity; the group this domain is built around |
| `instrument_type` | string | micrometer | `validated` | the equipment class; the first folder level |
| `calibration_date` | string | 2026-02-03 | `direct` | a labeled date on the certificate |
| `due_date` | string | 2027-02-02 | `direct` | a labeled due or valid-until field; the field that makes the record actionable |
| `calibration_status` | string | in tolerance | `direct` | a labeled as-found or verdict field; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `calibration_laboratory` | string | an accredited laboratory | `validated` | §3.8 "The system must separate roles that happen to contain the same entity type." — the laboratory, the instrument owner and the manufacturer are three roles |
| `traceability_reference` | string | accreditation certificate 0123 | `validated` | what makes the measurement mean anything; corroborated as under recognition |
| `uncertainty_statement` | string | stated at k=2 | `direct` | a labeled uncertainty field; recorded for explanation, never a folder dimension |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a calibration-certificate header: a certificate-number field together with an instrument-identifier field and a traceability or accreditation statement — 'traceable to' | 'accredited to ISO/IEC 17025' | a national metrology institute name
- an as-found and as-left column pair in a §2.3 table together with an instrument identifier. The as-found / as-left pairing is unique to calibration and is what separates it from inspection
- a calibration-due field together with an instrument-register row

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a supplier certificate whose instrument identity is only a serial number and a photograph
- deciding whether the calibrated object is a shop gauge, a test rig or a production machine

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an accreditation body name inside a document that merely cites it
- a due-date field — every controlled document in this slice has one
- an instrument serial number

### Work types

`calibration certificate`, `calibration register`, `as-found and as-left record`, `out-of-tolerance notification`, `impact assessment`, `gauge study`, `verification check record`, `calibration procedure`

### Grouping reasons (§4)

- one instrument across its calibration history. This is the one place in the slice where the newest record does NOT supersede the last: an out-of-tolerance finding makes every measurement taken since the previous calibration suspect, so the history is a genuine time series and not a §3.11 version family
- one out-of-tolerance event across its notification, impact assessment and recall of affected results

### Template (§5)

`instrument type → instrument`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child" — the instrument folder holds its certificate history, which is how metrology is actually filed. That risks §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." for instruments calibrated once, so the instrument level should be offered rather than imposed: §5.9 "It should recommend flattening when a dimension does not materially improve retrieval."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| qual.inspection-record | calibration measures the instrument, inspection measures the part, and the tables look the same | §3.8 "The system must separate roles that happen to contain the same entity type." |
| mro.asset-record | instruments are assets, in a register with the same columns | §3.11 "One file may hold facts from more than one domain without losing information." |
| mfg.tooling-fixture | gauges are tools and calibrated items under one number | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.verification-validation | the test rig's calibration certificate is part of the test evidence and is filed with the report | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `qual.nonconformance-capa` — Nonconformance and corrective action

Something did not conform: the record of it, and of what was done so that it stops.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `product` | string | Hawk Mk2 | `validated` | the product affected; the first folder level |
| `nonconformance_reference` | string | NCR-2026-0087 | `validated` | the record's identity |
| `affected_item` | string | HK2-4471-01 | `validated` | the part, lot or process that did not conform |
| `defect_category` | string | dimensional | `validated` | the classification that makes trending possible; this is the field that turns records into information |
| `disposition` | string | use as is | `direct` | a labeled disposition field whose values are the material-review vocabulary; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `capa_reference` | string | CAR-2026-0031 | `validated` | the corrective action raised from it, which is a different record with a different life |
| `status` | string | closed, effectiveness verified | `direct` | a labeled status field |
| `source` | string | internal audit | `validated` | audit, inspection, customer complaint or field failure — where the finding came from |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a nonconformance or corrective-action reference label together with a disposition field whose values are the material-review vocabulary — 'use as is' | 'rework' | 'repair' | 'scrap' | 'return to supplier'
- a corrective-action heading structure: a containment heading together with a root-cause heading and an effectiveness-check heading
- a §2.3 finding table pairing a requirement or clause column with a finding column and an action column, under a reference number

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a complaint email that is a nonconformance in substance with no record raised
- distinguishing a concession from a nonconformance disposition when both resolve to 'use as is'

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- 'NCR' — also a company name and a common abbreviation
- the word 'defect'
- a reference number

### Work types

`nonconformance report`, `material review board record`, `corrective action request`, `containment plan`, `root-cause statement`, `effectiveness check`, `concession or deviation`, `supplier corrective action request`

### Grouping reasons (§4)

- one nonconformance across its containment, cause, action and effectiveness check
- one affected item across every nonconformance raised against it
- one defect category across the records that share it — a trending group rather than a document group

### Template (§5)

`product → artifact type`

Time first: **no**

one folder per reference number is §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| qual.failure-analysis-rca | the failure analysis is the technical investigation inside the corrective action | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.change-order | a corrective action that resolves into a design change | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.warranty-claim | a field failure is a customer claim and an internal nonconformance simultaneously | §3.11 "One file may hold facts from more than one domain without losing information." |
| hse.incident-record | a safety incident and a quality nonconformance share the containment-cause-action structure exactly, and one event is often both — but only one of them carries §8.4's medical information | §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `qual.failure-analysis-rca` — Failure analysis and root cause investigation

Why one specific thing broke — the technical investigation, its evidence and its conclusion.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `product` | string | Hawk Mk2 | `validated` | the product the failed item belongs to; the first folder level |
| `failed_item` | string | HK2-4471-01 serial 0122 | `validated` | the specific article investigated — a serial, not a part type |
| `failure_mode` | string | fatigue crack initiation at the fillet | `validated` | the mechanism concluded; the field that makes investigations comparable |
| `analysis_technique` | string | SEM fractography | `validated` | the method used; a labeled or headed field |
| `event_reference` | string | NCR-2026-0087 | `validated` | the nonconformance, claim or incident this investigation belongs to |
| `sample_reference` | string | sample 3, longitudinal section | `validated` | which specimen produced which evidence, without which the report is unreviewable |
| `conclusion_state` | string | root cause identified | `llm_supported` | §3.13 "An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation." — whether an investigation actually concluded or merely reported is a reading of the prose and is frequently ambiguous |
| `analysis_date` | string | 2026-05-02 | `direct` | a labeled date field |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a failure-analysis title term ('failure analysis' | 'root cause analysis' | 'fractography' | '8D' | 'teardown') together with a failed-item identifier and an evidence heading — 'examination' | 'findings' | 'metallography' | 'micrograph'
- an 8D structure in headings: a containment section together with a root-cause section and a prevent-recurrence section, with a part number in the header block
- a laboratory report header naming a technique together with a sample reference and a submitting reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an investigation written as narrative with no method named anywhere
- deciding whether a materials investigation is a failure analysis or a research characterisation study — the instrument output is byte-for-byte the same kind of file

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- 'RCA' — also a company name and a connector type
- a micrograph image: it is the most recognisable artifact in the domain and proves nothing about purpose
- the words 'root cause' inside a procedure that merely requires one

### Work types

`failure analysis report`, `8D report`, `five-why or fishbone worksheet`, `fractography set`, `metallurgical report`, `teardown report`, `fault-tree instance`, `evidence custody note`

### Grouping reasons (§4)

- one failure event across its samples, techniques and report
- one failure mode across the events that share it
- one returned unit across its inspection, analysis and disposition

### Template (§5)

`product → artifact type`

Time first: **no**

§5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.risk-analysis-fmea | predicted failure and observed failure, in the same vocabulary and opposite directions in time | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.nonconformance-capa | the investigation is a section of the corrective action and a document in its own right | §3.11 "One file may hold facts from more than one domain without losing information." |
| res.instrument-output | SEM, XRD and tensile output are identical whether the purpose is engineering or research, and §3.9 "The documents are content-incoherent but purpose-coherent." | §3.9 "The documents are content-incoherent but purpose-coherent." |
| hse.incident-record | when the failure hurt someone the investigation is also a safety investigation, and §8.4's medical information enters a document that would otherwise be purely technical | §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `qual.supplier-qualification` — Supplier qualification and audit

Deciding whether a supplier may be used, and keeping the evidence that they still may.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." The role problem it exists to solve is design-named: §3.8 "The system must separate roles that happen to contain the same entity type."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `supplier` | string | a contract machinist | `validated` | §3.8 "The system must separate roles that happen to contain the same entity type." — in one audit report the supplier, the customer, the certification body and our own organisation all appear as organisation names, and only their roles distinguish them |
| `supplier_site` | string | Wuxi plant | `validated` | approval is granted to a site, not to a company, and this distinction is routinely lost |
| `risk_category` | string | critical | `validated` | the criticality band that decides how much evidence is required; the first folder level |
| `qualification_status` | string | approved with conditions | `validated` | the current standing |
| `scope_of_supply` | string | machined aluminium parts up to 400mm | `llm_supported` | §3.13 "An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation." — scope is prose, and its edges decide whether a given order is covered |
| `audit_reference` | string | SA-2026-11 | `validated` | the audit's identity |
| `approval_expiry` | string | 2027-03-31 | `direct` | a labeled expiry field |
| `quality_agreement_reference` | string | QA-2024-08 | `validated` | the contractual quality terms, which are a different document from the commercial contract |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a supplier-audit report header: an audited-organisation field together with an audit-scope field and a §2.3 finding table, where the audited organisation is not our own — the role test is the corroboration
- an approved-vendor-list row set pairing a supplier column with an approved-scope column and an approval-date column
- a supplier questionnaire whose §2.3 table pairs a question column with a supplier-response column, together with a named supplier organisation

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- correspondence that grants or withdraws approval without a form
- deciding which organisation in a document is the supplier and which is us — §3.8 "The system must separate roles that happen to contain the same entity type.", and this is the domain where getting it backwards is most damaging

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an organisation name — §3.8 "The system must separate roles that happen to contain the same entity type." applies with full force: the same company is a supplier, a customer, an employer, a certification body and a merely cited organisation
- the word 'audit'
- a certificate number

### Work types

`supplier questionnaire`, `supplier audit report`, `approved vendor list entry`, `quality agreement`, `part approval submission`, `supplier scorecard`, `supplier corrective action request`, `qualification certificate set`

### Grouping reasons (§4)

- one supplier site across its qualification file
- one qualification cycle across questionnaire, audit, findings and approval
- one part approval across the inspection, process and capability evidence it required

### Template (§5)

`risk category → supplier → artifact type`

Time first: **no**

supplier does not lead: §3.8 "A folder should not become a collection point for everything produced by the same person or organization." A directory per supplier is that, unless the relationship has real substance. Risk category leads, then supplier, then artifact type, which is §5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.vendor-management | the finance slice holds the commercial relationship and this holds the technical approval; the same audit report and the same quality agreement belong to both | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.inspection-record | supplier first articles are inspection records under an approval purpose | §3.9 "The documents are content-incoherent but purpose-coherent." |
| qual.nonconformance-capa | supplier corrective action requests belong to both files | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.automotive-program | part approval submissions are programme artifacts and supplier-approval artifacts at once | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase §2.9 "potentially sensitive" is the only marking made here. Supplier onboarding packs routinely carry the supplier's bank details and tax registration, which §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." reaches directly. The accepted finance slice marks its vendor-management entry on the same evidence, and this entry follows it rather than diverging. The handling CLASS is P7's (§8.4) and is not set.

---

## `qual.warranty-claim` — Warranty claims and field-return analysis

A customer says it failed in service: the claim, the returned part, and what the pattern across claims means.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `product` | string | Hawk Mk2 | `validated` | the product claimed against; the first folder level |
| `claim_reference` | string | WC-2026-4471 | `validated` | the claim's identity |
| `serial_number` | string | 0122 | `validated` | the individual unit, which is what makes claim analysis possible at all |
| `failure_symptom` | string | intermittent stall under load | `llm_supported` | §3.13 "An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation." — a customer-reported symptom is prose and mapping it to a failure mode is exactly the interpretation a rule cannot do safely |
| `claim_status` | string | accepted | `direct` | a labeled status field |
| `in_service_date` | string | 2025-11-04 | `direct` | a labeled date field; with the claim date it gives time-in-service, which is the whole point of the record |
| `claim_date` | string | 2026-06-12 | `direct` | a labeled date field |
| `returned_part_disposition` | string | returned for analysis | `validated` | what happened to the part, which links this domain to `qual.failure-analysis-rca` |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a claim-reference label together with a serial-number field and a warranty term — 'warranty claim' | 'return authorisation' | 'in warranty' | 'goodwill'
- a claim-analysis table pairing a failure-code or symptom column with a serial or build-date column and a claim-cost column
- a return-authorisation form pairing a customer block with a product and serial block and a reported-fault field

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a customer email describing a failure with no claim ever raised
- reading a customer's symptom description into an engineering failure mode

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- 'RMA' — a three-letter token
- a serial number
- a customer name: §3.8 "The system must separate roles that happen to contain the same entity type.", since the customer, the dealer, the manufacturer and the insurer all appear as organisations in one claim

### Work types

`warranty claim`, `return authorisation`, `returned-part inspection`, `warranty analysis report`, `field-failure report`, `campaign or recall notice`, `goodwill decision`, `claim rejection letter`

### Grouping reasons (§4)

- one claim across its authorisation, return, inspection and decision
- one product across one claim period
- one failure mode across the claims that share it — the group that turns claims into engineering information

### Template (§5)

`product → artifact type`

Time first: **no**

§5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| qual.failure-analysis-rca | the returned part goes to the laboratory and the report belongs to both | §3.11 "One file may hold facts from more than one domain without losing information." |
| mro.field-service-report | the engineer's visit and the commercial claim are two records of one failure | §3.11 "One file may hold facts from more than one domain without losing information." |
| fin.insurance | a claim under a policy and a claim under a warranty have the same shape and different counterparties | §3.8 "The system must separate roles that happen to contain the same entity type." |
| qual.nonconformance-capa | a field failure is a claim outward and a nonconformance inward | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase §2.9 "potentially sensitive" is the only marking made here. A warranty claim carries an identified customer — name, address and purchase record — and where the failure caused harm it carries an injury account, which is §8.4's medical information. §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." reaches the purchase and payment side as well. The handling CLASS is P7's (§8.4) and is not set.

---

## `mro.asset-record` — Asset register and equipment records

The identity of a physical asset — what it is, where it is, and everything permanently true about it.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `asset_identifier` | string | PMP-0114 | `validated` | the asset's identity, which in most plants is the same string space as the process tag — see the collision below |
| `asset_type` | string | centrifugal pump | `validated` | the equipment class; the second folder level |
| `manufacturer` | string | a pump maker | `validated` | §3.8 "The system must separate roles that happen to contain the same entity type." — the manufacturer, the installer and the maintainer are three roles |
| `model` | string | CN-80/200 | `validated` | the model designation from the nameplate |
| `serial_number` | string | SN-448120 | `direct` | read from the nameplate or a labeled field; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `site` | string | Teesside plant | `validated` | the physical location; the first folder level |
| `parent_asset` | string | feed pump skid | `validated` | the asset hierarchy, which is a structural relation exactly like an assembly BOM |
| `criticality` | string | critical | `validated` | the band that decides maintenance and spares strategy |
| `installation_date` | string | 2026-06-30 | `direct` | a labeled commissioning or installation date |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- an asset-register row set in a §2.9 spreadsheet: an asset-identifier column beside a location column beside a manufacturer or model column
- a nameplate transcription — a manufacturer and model pairing together with a serial-number label and a rating field — in a §2.3 table or an OCR'd photograph, which is the normal source and is why §2.7 "OCR is not merely a rescue tool for scanned PDFs."
- an asset-identifier label ('asset no' | 'tag no' | 'equipment no' | 'plant no') together with a location or parent-asset field

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an equipment list embedded in a handover manual with no header row
- deciding whether a tag identifies an asset, a drawing or a process line — in most plants the same tag does all three

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a serial number — §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.", and a serial number has that shape
- a manufacturer name
- an asset tag alone: this collides inside the catalogue as well as outside it, because `eng.process-flow-pid`'s equipment tags are frequently the identical string

### Work types

`asset register entry`, `nameplate record`, `equipment datasheet`, `asset hierarchy list`, `criticality assessment`, `transfer or disposal record`, `asset warranty record`, `condition assessment`

### Grouping reasons (§4)

- one asset across its whole life — register entry, manual, maintenance history, spares and disposal
- one site across its asset hierarchy, a parent-child structure rather than a flat list
- one commissioning handover across the assets it created

### Template (§5)

`site → asset type → asset`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child" — the asset folder is the natural home of everything about one machine. Where a corpus holds one or two documents per asset the asset level should be flattened: §5.9 "It should recommend flattening when a dimension does not materially improve retrieval."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.commissioning-handover | handover is where the asset record is born and the nameplate data comes straight out of the pack | §3.11 "One file may hold facts from more than one domain without losing information." |
| eng.process-flow-pid | the equipment list and the asset register describe the same equipment under two identifier schemes | §3.8 "The system must separate roles that happen to contain the same entity type." |
| pers.vehicle | a personal vehicle is an asset with exactly this record shape and none of the industrial context | §3.11 "One file may hold facts from more than one domain without losing information." |
| soft.it-asset-inventory | the software slice's IT register has identical columns; the separating signal is whether the asset carries a maintenance regime or a software estate | §3.8 "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `mro.maintenance-work-order` — Maintenance work orders and history

A job done to an asset: the request, the instruction, the work performed and the history it becomes.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site` | string | Teesside plant | `validated` | the location; the first folder level |
| `asset_identifier` | string | PMP-0114 | `validated` | what was worked on — this domain's subject, and the group everything hangs from |
| `work_order_reference` | string | MWO-51022 | `validated` | the job identity; the same number space as production orders, which is the collision below |
| `maintenance_type` | string | preventive | `validated` | preventive, corrective, breakdown, shutdown or condition-based — the classification the whole discipline turns on |
| `trade` | string | mechanical fitter | `validated` | the discipline that did the work; a search field |
| `completion_state` | string | complete | `direct` | a labeled status field; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `scheduled_date` | string | 2026-07-15 | `direct` | a labeled planned date |
| `completion_date` | string | 2026-07-17 | `direct` | a labeled actual date |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a work-order reference label together with an asset-identifier field and a maintenance-type field — 'preventive' | 'corrective' | 'breakdown' | 'shutdown' | 'planned maintenance'
- a preventive-maintenance schedule table pairing an asset column with a task-description column and a frequency column
- a completion block ('work carried out' | 'parts used' | 'time taken' | 'completed by') together with an asset identifier

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a handwritten job card, which is still the normal artifact in much of this field
- distinguishing a maintenance work order from a production work order when the numbering overlaps and neither document names its issuing system

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- 'PM' — also a time abbreviation, a job title and a project-management abbreviation
- a work-order number
- a date

### Work types

`work order`, `preventive maintenance task list`, `job card`, `maintenance history extract`, `shutdown or turnaround plan`, `permit to work`, `parts-used record`, `condition-monitoring reading set`

### Grouping reasons (§4)

- one asset across its maintenance history — the group that gives an asset a story
- one shutdown across every work order raised inside it
- one work order across its request, execution and close-out

### Template (§5)

`site → asset → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child" §5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| mro.asset-record | the register entry and the history are two halves of one asset | §3.11 "One file may hold facts from more than one domain without losing information." |
| mfg.production-planning | both are work orders, in overlapping number ranges, with the same columns | §3.8 "The system must separate roles that happen to contain the same entity type." |
| hse.incident-record | permits to work and isolation records belong to maintenance and to safety at once | §3.11 "One file may hold facts from more than one domain without losing information." |
| mfg.work-instruction | a maintenance procedure and a shop instruction share the step-and-caution shape exactly | §3.8 "The system must separate roles that happen to contain the same entity type." |
| eng.aerospace-airworthiness | a service bulletin arrives as design data and is executed as a work order | §3.9 "The documents are content-incoherent but purpose-coherent." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `mro.spare-parts` — Spare parts and stock records

What is held, or should be held, so that a repair can happen — the stock side of maintenance.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site` | string | Teesside plant | `validated` | the stores location; the first folder level |
| `used_on_asset` | string | PMP-0114 | `validated` | what the part belongs to — the fact that makes a spares list navigable |
| `part_number` | string | SEAL-4471-M | `validated` | the part's identity |
| `part_description` | string | mechanical seal, cartridge | `direct` | a labeled description field; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `supplier` | string | the original equipment maker | `validated` | §3.8 "The system must separate roles that happen to contain the same entity type." — the maker of the part and the seller of the part are different roles |
| `stock_location` | string | stores bay C, bin 12 | `validated` | the corroborating field: a part number beside a bin location is a stock record and not a bill of materials |
| `criticality` | string | insurance spare | `validated` | the holding rationale, which is the difference between a spares strategy and a shopping list |
| `obsolescence_status` | string | last time buy announced | `validated` | the field that makes an old spares list urgent |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a spares list whose §2.9 spreadsheet headers pair a part-number column with a stock-location or bin column and a reorder or minimum-holding column — the stock-location column is the corroboration, since the part-number column alone makes a bill of materials, a purchase order or a catalogue equally well
- a recommended-spares heading in a handover or maintenance manual together with an asset identifier and a part-number column
- an obsolescence or last-time-buy notice naming a part number together with an affected-asset reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a spares recommendation written as prose in a supplier letter
- deciding whether a parts list is a spares holding, a bill of materials or a purchasing catalogue

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a part-number column — the single most reused table shape in this slice
- a quantity column
- a supplier name

### Work types

`recommended spares list`, `stock holding record`, `critical spares assessment`, `obsolescence notice`, `reorder record`, `stores issue record`, `interchangeability note`, `consignment stock agreement`

### Grouping reasons (§4)

- one asset across its spares
- one part number across its stock, sourcing and obsolescence records
- one obsolescence notice across the assets it strands

### Template (§5)

`site → asset → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.bill-of-materials | a recommended spares list is a filtered bill of materials with a stock column added | §3.11 "One file may hold facts from more than one domain without losing information." |
| biz.procurement-po | the reorder record and the purchase order are the same event on two sides | §3.8 "The system must separate roles that happen to contain the same entity type." |
| mro.asset-record | spares are held against an asset and appear in its record | §3.11 "One file may hold facts from more than one domain without losing information." |
| mfg.production-planning | shortage lists and stock reports share a table shape | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---

## `mro.field-service-report` — Field service reports

What an engineer found and did at a customer's site.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `customer` | string | a process operator | `validated` | §3.8 "The system must separate roles that happen to contain the same entity type." — the customer here is the subject of the work, not its author, which is why customer may lead the folder order where authorship never may |
| `site_location` | string | Teesside, unit 400 | `validated` | where the visit happened; the second folder level |
| `service_reference` | string | FSR-2026-0881 | `validated` | the visit's identity |
| `asset_identifier` | string | PMP-0114 | `validated` | what was worked on |
| `visit_date` | string | 2026-08-04 | `direct` | a labeled date field |
| `work_performed` | string | replaced seal, realigned coupling | `llm_supported` | §3.13 "An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation." — what was actually done is narrative in most reports and is the field a rule cannot extract safely |
| `outcome_state` | string | resolved | `direct` | a labeled outcome or status field |
| `parts_used` | list of strings | SEAL-4471-M | `direct` | a labeled parts table; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a service-report header: a customer field together with a site or address field and a visit-date field, plus a findings or work-performed section
- a signature-and-acceptance block ('customer signature' | 'work accepted by') together with an asset identifier and a date
- photographs whose §2.6 EXIF capture time and GPS cluster at one location on one date, alongside a report naming that site — §2.6 "Camera EXIF, GPS, and capture time can support deterministic photo-event proposals."

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a service narrative with no structured header at all, which is common when the report is an email
- deciding whether a visit was warranty, contract or chargeable: the report rarely says and the commercial answer lives elsewhere

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a GPS coordinate — §2.6 "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and the converse holds too: presence of GPS proves capture location, never purpose
- a customer name
- a date

### Work types

`field service report`, `site visit record`, `installation report`, `commissioning visit note`, `service acceptance sheet`, `site photographs`, `follow-up action list`, `service quotation`

### Grouping reasons (§4)

- one visit across its report, photographs and acceptance sheet
- one customer site across its service history
- one fault across the visits it took to close — a purpose group, since the reports are individually complete

### Template (§5)

`customer → site → artifact type`

Time first: **no**

customer leads here and nowhere else in this slice. §3.8 "A folder should not become a collection point for everything produced by the same person or organization." — the warning is about authorship, and in field service the customer is the SUBJECT of the work rather than its producer, which is precisely the role distinction §3.8 "The system must separate roles that happen to contain the same entity type." §5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| qual.warranty-claim | the visit and the claim are two records of one failure, with different counterparties | §3.11 "One file may hold facts from more than one domain without losing information." |
| mro.maintenance-work-order | an external service visit is a maintenance job seen from the supplier's side | §3.8 "The system must separate roles that happen to contain the same entity type." |
| career.consulting-engagement | for a sole practitioner the site visit is a consulting engagement record too | §3.11 "One file may hold facts from more than one domain without losing information." |
| pers.travel-record | the travel half of the visit — flights, hotels and expenses — is a travel record | §3.9 "The documents are content-incoherent but purpose-coherent." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase §2.9 "potentially sensitive" is the only marking made here. Two §8.4 categories are reached directly. The report identifies a customer contact and their premises, and site photographs carry EXIF location, which §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." names as GPS metadata. The handling CLASS is P7's (§8.4) and is not set.

---

## `hse.safety-case` — Safety cases and safety justification

The argued justification that a hazardous system is safe enough to operate, and the evidence beneath it.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site` | string | Teesside plant | `validated` | the installation the case covers; the first folder level |
| `system` | string | flare relief system | `validated` | the system the argument is about |
| `safety_case_reference` | string | SC-TS-004 | `validated` | the case's identity |
| `regulatory_regime` | string | a major-hazard regime | `validated` | the regime the case is submitted under. Jurisdiction-dependent — see the inherited question on `hse.incident-record` |
| `regulator` | string | the competent authority | `validated` | §3.8 "The system must separate roles that happen to contain the same entity type." — the regulator, the operator and the assessor are three roles |
| `hazard_reference` | string | HAZ-118 | `validated` | the hazard-log entry the section addresses |
| `argument_claim` | string | risk reduced so far as reasonably practicable | `llm_supported` | §3.13 "An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation." — a safety argument is prose by construction and its claim structure cannot be read by rule |
| `revision` | string | 6 | `direct` | a labeled revision field; a §3.11 version family whose superseded members remain legally live |
| `review_due` | string | 2027-09-30 | `direct` | a labeled periodic-review date |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a safety-case term ('safety case' | 'safety report' | 'safety justification' | 'safety argument' | 'hazard log') together with a facility or system name and a regulator or regime reference
- a hazard-log table pairing a hazard-reference column with a control column and a residual-risk column, together with a system name
- a safety-critical element list pairing an element column with a performance-standard column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a safety argument distributed across engineering reports with no case document to anchor it
- deciding whether a hazard analysis is design risk (`eng.risk-analysis-fmea`) or the safety case that consumes it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'safety' — it is in the title of a datasheet, a policy, a sign and a training slide
- an as-low-as-reasonably-practicable phrase inside a document that merely defines it
- a hazard reference

### Work types

`safety case or report`, `safety argument`, `hazard log`, `bow-tie analysis`, `safety-critical element list`, `performance standard`, `independent assessment report`, `regulator correspondence`, `periodic review record`

### Grouping reasons (§4)

- one facility across its case, hazard log and supporting evidence — a purpose group whose members are content-diverse
- one safety case across its revisions and periodic reviews
- one hazard across the analysis, control and verification that closes it

### Template (§5)

`site → system → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| eng.risk-analysis-fmea | the case argues from these analyses and reproduces their tables verbatim | §3.11 "One file may hold facts from more than one domain without losing information." |
| hse.incident-record | incident history is evidence inside the case, which is how §8.4's medical information enters it | §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." |
| hse.environmental-compliance | both are regulator-facing regimes with the same submission-and-review document shape | §3.8 "The system must separate roles that happen to contain the same entity type." |
| corp.regulatory-filings | the finance slice's general regulatory-filing entry covers the submission half of this | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase §2.9 "potentially sensitive" is the only marking made here. Two §8.4 categories are reached. A safety case is a regulator submission, which §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." covers as a legal record, and it quotes incident and injury history, which is medical information in the same list. The design's nearest handling of a document of this kind is §4.9 "Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold." The handling CLASS is P7's (§8.4) and is not set.

---

## `hse.incident-record` — HSE incident and near-miss records

Someone was hurt, or nearly was — the report, the investigation and what changed because of it.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site` | string | Teesside plant | `validated` | where it happened; the first folder level |
| `incident_reference` | string | INC-2026-0412 | `validated` | the record's identity |
| `incident_type` | string | near miss | `validated` | injury, near miss, dangerous occurrence, environmental release or property damage |
| `incident_date` | string | 2026-03-19 | `direct` | a labeled date field; with an incident this is the fact everything else is indexed on |
| `injury_state` | string | first aid, no lost time | `direct` | a labeled classification field. This is the field that makes the record sensitive, and it is why the entry carries §2.9's marking |
| `reportable_status` | string | reportable to the authority | `validated` | whether it must be notified. Jurisdiction-defined — see this entry's open question |
| `investigation_state` | string | closed | `direct` | a labeled status field |
| `corrective_action_reference` | string | CAR-2026-0031 | `validated` | the action raised, which lives in `qual.nonconformance-capa`'s vocabulary |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- an incident-report field set: an incident-date field together with a location field and an injury or near-miss classification field
- an incident-reference label together with an investigation heading set — 'immediate cause' | 'underlying cause' | 'root cause' | 'actions'
- a regulator-notification form naming a reportable category together with a site and a date

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an account of an incident in an email or a shift log with no form behind it
- deciding whether an event is a safety incident, a quality nonconformance or an environmental release — one event is frequently all three, and §4.9 "A file may validly belong to more than one accepted group"

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'incident' — the software slice uses it for outages and this one for injuries, and the two corpora meet in any technology manufacturer
- a date and a site
- 'near miss' inside training material, which is where the phrase most often appears

### Work types

`incident report`, `near-miss report`, `investigation report`, `witness statement`, `regulator notification`, `corrective action record`, `safety alert`, `return-to-work record`

### Grouping reasons (§4)

- one incident across its report, investigation, statements and actions
- one site across one reporting period
- one hazard across the incidents that keep arising from it

### Template (§5)

`site → year → artifact type`

Time first: **no**

§5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." — site leads and the year follows, which is also how incident files are kept. §5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| qual.nonconformance-capa | the containment-cause-action structure is identical; only one of the two carries injury information | §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." |
| hse.safety-case | incident history is evidence inside the case | §3.11 "One file may hold facts from more than one domain without losing information." |
| med.occupational-health-screening | the healthcare slice holds the injured person's medical record and this holds the event record. §3.8 "The system must separate roles that happen to contain the same entity type." is what keeps them apart, and conflating them would put a named individual's health record into a plant file | §3.8 "The system must separate roles that happen to contain the same entity type." |
| legal.litigation-dispute | an incident that becomes a claim is a safety record and a legal record at once | §3.11 "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase §2.9 "potentially sensitive" is the only marking made here. This is the clearest §8.4 hit in the slice. An incident record names an identified individual and describes their injury, and §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." names medical information explicitly; a reportable incident then becomes a regulator submission and often a claim, which reaches legal records in the same list. The handling CLASS is P7's (§8.4) and is not set.

### Open question — for Joseph, unresolved

REPORTABILITY IS JURISDICTION-DEFINED and the design states no jurisdiction anywhere. The same event is reportable to the national authority in one country, recordable under a different scheme in another, and neither elsewhere; the notification form, the timescale and the categories all differ. This entry is written functionally, with a `reportable_status` field rather than any jurisdiction's vocabulary, which is the same holding position the accepted finance slice takes. Whatever Joseph decides for that slice's jurisdiction question governs this entry, `hse.environmental-compliance`, `hse.safety-case` and `eng.civil-structural`'s design codes as well.

---

## `hse.environmental-compliance` — Environmental permits and monitoring

Permission to affect the environment, and the periodic proof that the permitted limits were kept.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site` | string | Teesside plant | `validated` | the permitted installation; the first folder level |
| `permit_reference` | string | EPR/AB1234CD | `validated` | the permit's identity |
| `regulator` | string | the environment agency | `validated` | §3.8 "The system must separate roles that happen to contain the same entity type." — the regulator, the operator and the sampling laboratory are three roles |
| `permitted_activity` | string | combustion, 20MW thermal | `validated` | what the permit allows, which is the scope everything else is measured against |
| `emission_point` | string | stack A2 | `validated` | the sampling or release point; the fact that ties a monitoring result to a permit condition |
| `monitored_parameter` | string | total suspended solids | `validated` | what was measured |
| `reporting_period` | string | Q2 2026 | `direct` | a labeled period field |
| `compliance_state` | string | compliant | `direct` | a labeled compliance or exceedance field; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `permit_expiry` | string | 2031-03-31 | `direct` | a labeled expiry or review date |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- a permit-reference label together with a regulator name matched on a word boundary and a condition schedule or permitted-activity block
- a monitoring return: a §2.9 spreadsheet or §2.3 table pairing a parameter column with a sampling-point column and a limit column, together with a site name
- a laboratory analysis certificate naming a sampling point and a sample date, whose client site matches a permitted site

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a consultant's environmental report that is compliance evidence but names no permit
- deciding whether a monitoring result belongs to an environmental permit, a process control record or a research dataset

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a parameter name — 'pH', 'COD' and 'NOx' appear in process design, research and procurement alike
- a regulator name inside a document that merely cites the regime
- a sample date

### Work types

`environmental permit`, `permit variation`, `condition schedule`, `monitoring return`, `laboratory analysis certificate`, `emissions inventory`, `waste transfer note`, `non-compliance notification`, `environmental impact assessment`

### Grouping reasons (§4)

- one permit across its variations — a §3.11 version family in which a superseded condition schedule is still legally significant
- one site across one reporting period
- one emission point across its monitoring history, which like calibration is a genuine time series rather than a version family

### Template (§5)

`site → permit → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| admin.licences-permits | the finance slice's general licence entry; the separating signal is a monitored parameter and a regulator-set limit | §3.11 "One file may hold facts from more than one domain without losing information." |
| hse.safety-case | both are regulator-facing regimes with one document shape | §3.8 "The system must separate roles that happen to contain the same entity type." |
| eng.process-flow-pid | emission points are drawn on the P&ID and licensed on the permit, under the same tag | §3.11 "One file may hold facts from more than one domain without losing information." |
| res.dataset | environmental monitoring data is a dataset in every technical respect; only the obligation behind it differs | §3.9 "The documents are content-incoherent but purpose-coherent." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase §2.9 "potentially sensitive" is the only marking made here. A permit is a regulator-issued authorisation and a non-compliance notification opens an enforcement process; both are legal records in §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records.". The accepted finance slice marks its licences-and-permits entry the same way, and this entry follows it. The handling CLASS is P7's (§8.4) and is not set.

---

## `hse.energy-audit` — Energy audits and efficiency surveys

A survey of how much energy a site or system uses, and what would reduce it.

**Provenance:** **proposal**

**Cite:** New. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site` | string | Teesside plant | `validated` | the audited location; the first folder level |
| `assessed_system` | string | compressed air | `validated` | the system surveyed; the second folder level, because one site is audited system by system |
| `audit_reference` | string | EA-2026-03 | `validated` | the audit's identity |
| `audit_scheme` | string | an energy management standard | `validated` | the scheme the audit is done under, where there is one |
| `audit_date` | string | 2026-02-18 | `direct` | a labeled date field |
| `baseline_period` | string | calendar year 2025 | `direct` | a labeled baseline field, without which no saving can be verified |
| `measure` | string | variable-speed drive on compressor 2 | `llm_supported` | §3.13 "An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation." — a recommended measure is prose in most reports and needs interpretation to become a comparable record |
| `auditor_organisation` | string | an energy consultancy | `validated` | §3.8 "The system must separate roles that happen to contain the same entity type." — the auditor and the audited are different roles |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.5):

- an energy-audit term ('energy audit' | 'energy survey' | 'energy performance' | 'energy management system') together with a site name and a consumption or measures table
- a measures table pairing a recommendation column with a saving column and a payback column, together with a site or system name
- a sub-metering export whose §2.9 spreadsheet headers pair a meter column with a period column and a consumption column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an energy discussion inside a wider sustainability or annual report
- deciding whether consumption data is an audit input, a utility bill or a process record

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an energy-unit token — it appears on every utility bill in the personal slice
- the word 'energy'
- a site name

### Work types

`energy audit report`, `measures register`, `sub-metering data`, `energy performance certificate`, `savings verification report`, `utility consumption extract`, `carbon reporting return`

### Grouping reasons (§4)

- one site across one audit cycle
- one measure from recommendation to verified saving
- one assessed system across its baseline, survey and follow-up

### Template (§5)

`site → assessed system → artifact type`

Time first: **no**

§5.5 "a parent dimension should provide the context required to understand the child"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.utilities | a domestic energy audit and a householder's utility file are the same document set: an energy performance certificate, meter readings and a measures list, with no organisation behind them | §3.11 "One file may hold facts from more than one domain without losing information." |
| hse.environmental-compliance | carbon reporting is an energy record and a regulatory return | §3.11 "One file may hold facts from more than one domain without losing information." |
| mro.asset-record | the measures register names assets and proposes work on them | §3.11 "One file may hold facts from more than one domain without losing information." |
| qual.management-system | an energy management system has the same audit-and-review shape as a quality one | §3.8 "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`none` — No §2.9 marking. Nothing in this domain's typical file reaches a category §8.4 "The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records." — which is the honest reading, and also the slice-wide finding recorded on `eng.engineering-project`: the design's corpus list has no concept of commercial confidentiality, trade secrets or export-controlled technical data, which are the restrictions that actually govern this supercategory. No handling class is set; handling classes are P7's (§8.4).

---
