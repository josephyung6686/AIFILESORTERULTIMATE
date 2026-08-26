# Research memo — `engineering.material-specification`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/engineering.material-specification.json`
Roster row: template on the fieldless `engineering` schema, `parent_id: null`, placeholder launch
Absorbed legacy row: `eng.component-datasheet`

## Result

Accept the node. It survives the charge on two of the node test's three legs, and the leg it survives most decisively is the one that matters: **the engineering schema's default template cannot activate on this row's files at all.** Every fixture in the file list would fail the schema's own detection signals and fall to Independent Records. That is not a subset of the default; it is the default's blind spot.

`fields`, `proposed_fields` and `template.dimension_order` stay empty under PR-6. The researched dimension inversion is recorded in prose for R1c, not serialized.

---

## The charge — the strongest case that this row should not exist

I put the case against the row first, and it is a genuinely strong one. Three prosecutions, in descending order of force.

**Prosecution 1 — it is a value of the schema's own enum, not a node.** This is the strongest attack and it comes from the schema anchor itself. `engineering.json` lists, verbatim in its `work_types[]` array, the entry **`"material or component specification"`**. The schema has already declared my row's subject to be a *value* of the proposed `engineering_artifact_type` field. The brief's node test is explicit that work types are values, and the stamped prompt says so twice: "Work types are values" and "the only 'difference' is work types or file extensions — those are values and `SOURCE_TYPES`, not nodes." On its face this row is `engineering_artifact_type = material specification`, which is exactly the 574's original mistake: minting a node for a dropdown option.

**Prosecution 2 — it is a document type.** "Specification" is a document-type word. A row whose membership test is "the document is called a specification" is a `work_type` in a trench coat, and the brief names document-type words as never-alone evidence that can never activate a row.

**Prosecution 3 — it is a duplicate of `engineering.requirements-specification`.** Both rows are "a document that states what something must be, and how conformance will be shown." Both use `shall` clauses, an issue letter, a referenced-document list and a verification-method column. If the only difference is whether the specified thing is a system or a substance, that is a value of a topic field, not two nodes.

### Defeating the charge

**Against Prosecution 1.** A value and a template can share a name and still be different objects, and CONNECTION.md §2 gives the discriminator: "A **template** row exists only if its detection signals, recommended dimensions, or privacy rules differ from its schema's default template." The test is not *is there a matching enum value* but *does the schema's default behaviour already handle these files correctly*. Here it demonstrably does not.

The engineering schema's `node_test.why` states its decisive difference in its own words: "The decisive difference is configuration identity: engineering files say which designed item and controlled definition a requirement, drawing, analysis, change or verification result belongs to." Every deterministic signal the schema lists is built on that relation — "an identified item or assembly, drawing identifier, revision/issue slot"; "for an identified system or item"; "to one identified item or released baseline"; "a parent assembly identifier".

A material or special-process specification **contains no design item, by construction, and that is the point of the artifact.** AMS 2700 (passivation of corrosion-resistant steels), MIL-DTL-5541 (chemical conversion coatings on aluminium) and an in-house anodize spec like the `MS-4120` fixture are written once, deliberately item-independent, and invoked by hundreds of unrelated parts across decades and across programmes. If a specification named a design item it would be useless as a specification.

The consequence is concrete rather than rhetorical: run `MS-4120 Rev D`, `PS-217 Rev 3`, the `LM317T` datasheet and the `Approved Materials and Processes List` through the schema's default detection signals and **none of them activate the engineering schema.** They have no title block with an item, no requirements table with an item column, no BOM parent/child, no verification matrix keyed to requirement identifiers for an item. They fall through to Independent Records. A whole coherent class of engineering material would be invisible to the engineering schema. That is a detection-signal difference of the strongest available kind — not "different enough", but "the default returns the wrong answer on all of it".

**Against Prosecution 2.** The row does not fire on the word. The node's `never_alone` list explicitly refuses "the words specification, spec, material, coating, process, grade, datasheet, TDS or standard alone", and refuses a specification-shaped identifier alone, a material designation alone, and a properties table alone. What fires is a *relation*: a specified object that is a material/component/process, joined to an acceptance criterion, joined to a named test method, with no measured value and no lot identity. The `SDS_Acetone` fixture proves the row is not word-driven — it is entirely about a material, has a property table, and is refused.

**Against Prosecution 3.** The two rows differ on the specified object, and that difference has operational consequences rather than being a topic label. A requirements specification is written for one system, is born and dies with that system's programme, and is organized under it. A material specification is written *against* all systems, outlives every programme that invokes it, and is destroyed as an artifact if it is filed under one. That is why the recommended dimension order inverts (below) rather than merely reordering. The two also fail differently: the requirements-spec failure is missing traceability; this row's failure is working to a superseded issue of a live document. I authored the boundary reciprocally with a shared fixture rather than asserting separation.

**Verdict: not a work_type value, not a document type, not a duplicate.** Accept.

I also tested the row against the remaining charge categories for completeness. It is not a lifecycle stage — a specification has issues, not gates, and it is not a phase of anything. It is not a medium, a length or a file format — its fixtures span `text_document`, `spreadsheet`, `image`, `ocr`, `email`, `archive` and `opaque_binary`. It is not an organisation name — supplier and standards-body names are explicitly listed as never-alone. It is not defined by an absence: "has no design item" is a *positive* structural property of specifications, not a residual catch-all, and the row states positively what it does have.

---

## The node test, all three legs

**Leg 1 — detection signals. DIFFERS, decisively.** Argued above. The schema keys on configuration identity; this row keys on a document-identity-plus-criterion-plus-method relation with an explicit absence of item and lot. Under the schema default these files do not activate.

**Leg 2 — recommended dimensions. DIFFERS, and inverts.** The schema's researched default, in its own `template.why`, is `project → design_item → lifecycle_stage → engineering_artifact_type`, with "revision_or_baseline stays metadata by default." This row recommends `specification identifier → issue/revision → specified-object class`, with **`project` and `design_item` absent from the order entirely**, and with the field the schema demotes to metadata promoted to near-primary. Filing a specification under the project that first invoked it is the observed failure of this world — the spec outlives the project, the next programme cannot find it, and re-authors it. And issue must be near the top because the defect mode here is manufacturing to a superseded issue of a live spec, which is why revision-bearing spec libraries exist at all. An inversion that drops two of the default's four levels and promotes its metadata field is not the default template.

**Leg 3 — privacy rules. PARTLY DIFFERS; the weakest leg, stated honestly.** `sensitivity` stays `potentially_sensitive`, identical to the schema, so this leg carries nothing on its own and I decline to inflate it. Two reasons differ in kind rather than in class. First, a plating bath chemistry or a heat-treat recipe *is* the trade secret, where a drawing merely shows a shape; defence and aerospace process specifications routinely carry distribution and export markings. Second — and this exposure genuinely does not exist for the schema's own drawings and models — a large share of this row's holdings are **third-party licensed documents** (purchased standard extracts, supplier datasheets) whose reproduction and redistribution are contractually restricted, so bulk transmission of members to a remote model is a licence question as well as a confidentiality one. Licence and handling are P7's; this row names the exposure and decides nothing.

CONNECTION.md's test is disjunctive ("or"). Two legs differ materially. Accept.

---

## Evidence base

Sources actually read: the standing brief; the stamped assignment; `planning/domains/nodes/legal.practice-matter-file.research.md` as the depth calibration; the full `engineering.json` schema anchor (its `node_test`, `recognition`, `work_types`, `proposed_fields`, `template`, edges, `sensitivity_why`, `open_question`); `planning/domains/CONNECTION.md` §2 (the node test table and the three bullets); `planning/domains/roster.json` (all `engineering.*`, `manufacturing.*`, `construction_property.*`, `research.*`, `code.*` rows, to find who competes with me); and `planning/00-database-agent-product-design.md` by targeted grep for the residual-library sentence only. Per the token discipline in my dispatch I did not stream `00`, `01` or `CONNECTION.md` in full.

`grep -rl "engineering.material-specification" planning/domains/nodes/` returned **nothing** — no landed row has yet argued a boundary against me. Every boundary below is therefore authored fresh and reciprocally, and R1c should expect matching text to appear on the neighbour side.

All four `falls_through_to` `design_cite` strings were grep-verified verbatim against line 120 of `00`. No other quotation is attributed to `00`. The CONNECTION.md sentence quoted in the node test is verbatim from its §2 bullet list. All other claims are marked `inference` in the JSON.

Real-world artifact families named as evidence (document types, not statistics): AMS 2700 passivation, AMS2750 pyrometry, MIL-DTL-5541 chemical conversion coatings, ASTM A276 stainless bar, EN 10204 3.1 inspection certificates, GHS 16-section safety data sheets, supplier technical data sheets, RoHS/REACH SVHC declarations, and the classical specification skeleton (Scope / Applicable Documents / Requirements / Quality Assurance Provisions / Preparation for Delivery / Notes). No thresholds, counts or statistics are asserted anywhere.

---

## Files considered and rejected

The JSON's sixteen fixtures split observations from facts. This section records the reasoning for the rejections, which is the part a fixture list cannot show.

- **`AMS2750G - Pyrometry.pdf`** — rejected to `engineering.standards-library`. It is normative, has shall clauses, an issue letter and a referenced-document list, and my own `PS-217` fixture cites it. It is rejected on **issuer role**: a standards body published it, the holder authored nothing, and its licence notice restricts reproduction. Contested at NJ-MS-2.
- **`Material Test Report - Heat 4471822 - 316L bar - EN 10204 3.1.pdf`** — the primary collision fixture, treated at length below.
- **`SDS_Acetone_2026-03_EN-GB.pdf`** — rejected. This is the fixture that disproves "the row fires on material words". It is entirely about a material and its section 9 is a physical-and-chemical-properties table. It is rejected because its purpose is hazard communication to a workforce, evidenced by the sixteen numbered GHS headings, first-aid measures and exposure controls, and because it contains no acceptance criterion, no sampling provision and no test method for procurement. It routes to Independent Records, and its workplace role belongs to the manufacturing HSE and site-safety worlds, not here.
- **`Materials Delivery Note 88231 - 316L bar 20mm - signed.pdf`** — rejected to `construction_property.materials-delivery`. Grade token `316L` matches my world exactly; quantities, a purchase-order reference and a signature of receipt make it transactional. Marked `group_without_copying_facts: true` so it may sit near an accepted specification neighbourhood without acquiring a specification identifier.
- **`Anodic layer thickness vs seal time - study writeup.docx`** — rejected to `research`. It measures the exact property my `MS-4120` fixture specifies and recommends changing it. Rejected because it has no document identifier, no issue and no approval block, and because a recommendation is not a normative requirement. It is `also_holds_with: research` if it later becomes qualification evidence for an issue.
- **`Deviation Request DR-0912`** — *not* rejected, but explicitly kept out of `engineering.change-order`. A change order alters a released definition; a deviation leaves the issue untouched and permits a bounded departure from it for named lots with an expiry. Recorded as `also_schema: manufacturing`.
- **`IMG_4451.HEIC`** — kept only as a never-alone trap. OCR yields a specification-identifier-shaped heading and a partial clause. Rejected as an activator: this is precisely the identifier-alone case, and EXIF gives a capture date that must not stand in for a specification date.
- **`Specification_Library_backup.7z`** — rejected to Unsupported or Encrypted. The filename contains the row's own name and licenses nothing.
- A **PLM or specification-management database, or a live standards subscription portal**, is a source system, not a file node. A bounded export with a readable manifest is represented (`SPEC_PACKAGE_MS4120_RevD.zip`); connector ingestion is a later security decision.
- **A marketing brochure with a properties table**, and **a purchasing catalogue whose codes resemble specification identifiers**, are both refused for the same reason as the TDS boundary: typical values and stock codes are not acceptance criteria.
- **Practice-level taxonomies** — an alloy taxonomy, a coating-process taxonomy, a standards-body list, a substance gazetteer — are deferred. Inventing one here would turn a placeholder into the industry catalogue J-IND forbids, and R4 owns gazetteer contents.

---

## The collision fixture

**`Material Test Report - Heat 4471822 - 316L bar - EN 10204 3.1.pdf`.**

It looks like this row's evidence in almost every respect a shallow classifier can see. It is about a material. It names a grade (`316L`). It cites a specification designation (`ASTM A276`). It contains a chemical-composition table and a mechanical-properties table whose row labels are identical to those in a material specification. It is signed and stamped by an inspector, which reads like an approval block.

**What discriminates it: measured values and lot identity.**

A specification states criteria and names methods; it carries no heat number, no lot, no batch, no serial, no quantity and no measured result. A mill certificate is the mirror image: a heat number (`4471822`), an order and item reference, a delivered quantity and dimension, and measured percentages and measured tensile, yield, elongation and hardness figures. The designation it cites is the *authority it is claiming to satisfy* — a citation is not membership. Reciprocally, `MS-4120 Rev D` stays here and does not become an inspection record merely because it names a test method.

Both sides carry this same fixture in `collides_with`, and the boundary text names the same bytes. Marked `group_without_copying_facts: true`: the certificate may join a specification neighbourhood as evidence without a specification identifier or issue being copied onto it.

A secondary collision worth naming: a supplier **Technical Data Sheet** and a **specification** are near-identical in appearance. The discriminator is *typical values versus acceptance criteria*, plus the absence of a sampling provision. A TDS informs; a specification imposes. This distinction is subtle enough that it sits in `needs_llm` rather than `deterministic`.

---

## Reciprocal boundaries

Every boundary is stated in both directions with the same fixture named on both sides. Full text is in the JSON; the seams are:

| Neighbour | Seam | Shared fixture, same on both sides |
|---|---|---|
| `engineering.standards-library` | issuer role: standards body/regulator vs. producer or in-house engineering | `AMS2750G-Pyrometry.pdf` → standards-library; `MS-4120 Rev D` → here. The `LM317T` datasheet is the contested case (NJ-MS-2) |
| `engineering.requirements-specification` | specified object: a system's behaviour vs. a substance/component/process | one `Product Specification.docx` whose functional sections are theirs and whose finish clauses *invoke* `MS-4120` — invocation links, it does not relocate |
| `manufacturing.inspection-record` | criteria + method + no lot vs. measured values + heat/lot identity | `Material Test Report - Heat 4471822` → theirs, on both sides |
| `manufacturing.supplier-qualification` | governs the material (any supplier) vs. governs the relationship (this supplier) | `RoHS/REACH Declaration - 5747299-1.pdf` — both may hold it on disjoint evidence |
| `manufacturing.work-instruction` | normative + invoked by many jobs + qualification regime vs. executional + one station + production-controlled | `PS-217 Rev 3` → here; `Furnace 2 - Load and Unload Steps Rev B.docx` → theirs, even repeating PS-217's temperatures verbatim |
| `construction_property.materials-delivery` | normative (criteria, method, issue, no quantity) vs. transactional (quantity, price, receipt signature, no criteria) | `Materials Delivery Note 88231` → theirs; grade token `316L` activates nothing |

`also_holds_with` is authored for `manufacturing` (a deviation is a production departure *and* a document in a spec's issue neighbourhood), `research` (a qualification report is knowledge *and* the evidence an issue rests on) and `engineering` (a substance declaration is material content *and* certification evidence for `engineering.product-certification`).

`role_split` is empty. The engineering schema declares no fields, so there is no field key to split a role across, and this row cannot author schema-level structure.

---

## Neighbours considered that got no edge

- **`code`** — a `must_consider_neighbors` entry, deliberately given no edge. The schema-level collision with code is about revision control, requirements and firmware baselines. None of that competes for *this* row's evidence: no material or process specification is confusable with a repository, and a `spec/` directory in a codebase is an API contract, not a coating spec. Recording a collision here would be theatre.
- **`engineering.drawing-package`** — no collision. A drawing's flag note invoking `MS-4120 Rev D` creates a *reference edge*, recorded in `grouping_reasons`: the drawing stays in the drawing package, the specification stays here, and neither copies the other's facts. If R1c finds a genuine same-evidence mutex it can add one, but the invocation relation is a link, not a contest.
- **`engineering.change-order`** — no collision; handled instead by keeping the deviation fixture explicitly out of it, since a deviation and a change order differ in whether the released issue moves.
- **`engineering.product-certification`** — coactivation, not mutex. Declarations legitimately serve both; making it a collision would force a false choice.
- **`engineering.bill-of-materials`** — no edge. The approved-materials list is the tempting overlap and is refused inside the fixture itself: no parent assembly, no child quantity, therefore not a BOM.
- **`manufacturing.nonconformance-capa`** — no edge. A nonconformance cites a specification the way a mill certificate does; the inspection-record boundary already carries the genuinely confusable evidence, and adding a second manufacturing mutex on the same seam would duplicate rather than clarify.
- **`research.reading-library`** — no mutex. A datasheet or standards extract with no accepted engineering association routes to Reading Inbox residually, which handles the case without an edge.

---

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `template.dimension_order: []`, `time_first: false`. All intentional under PR-6 and D1.

I explicitly **decline to mint** a `specification_id` key, even though this row's whole argument is that the specification document is its own organizing anchor and the schema's `design_item` cannot serve. Minting it would pre-empt R1c and would duplicate a decision the schema anchor already has open (NJ-ENG-1/NJ-ENG-3). It is raised as NJ-MS-3 instead. Candidates rejected for the same reason: `material`, `process`, `issue`, `specified_object`, `test_method`. The schema's existing proposals `engineering_artifact_type` and `revision_or_baseline` would cover part of this row if ratified; `project` is available canonically and is nonetheless recommended *out* of the order, which is itself a finding.

`time_first` is false. A specification has issues, not dates: effective date, approval date, revision date and filesystem date are four different things, and a chronological first level would scatter one specification's issue family across years — which is exactly the failure the row exists to prevent.

---

## Grouping without copied facts

Groups are bounded by an exact specification identifier plus issue. A group may contain the released document, its redlines, its approval email, its superseded copies, its referenced test methods, its qualification evidence and its deviations. Membership creates no facts on members: a referenced test-method extract does not acquire the parent specification's identifier, and a mill certificate that cites the spec does not become an issue of it. Sparse files (`coating thickness check.xlsx`, the shop-floor photo, the delivery note) may join a neighbourhood while carrying `group_without_copying_facts: true`. An archive manifest is read without extracting members, and no facts are asserted about members never opened.

---

## NEEDS-JOSEPH

One tension has no NJ item because it is not Joseph's to settle: licence restrictions on third-party specification content are real and materially constrain remote-model use, but licence is not a sensitivity value and this phase has no vocabulary for it. Named in `sensitivity_why`, left to P7.


1. **NJ-MS-1** — the roster hint calls this "an authored specification" yet assigns it `eng.component-datasheet` (received supplier documents). This row resolves the contradiction by making the specified object the unifying fact and authorship an observation. Confirm or reverse.
2. **NJ-MS-2** — reciprocal with `engineering.standards-library`: where does a supplier component datasheet live? (a) **issuer role decides** — standards body/regulator → standards-library, producer → here (recommended); (b) **authorship decides** — all received documents including datasheets → standards-library, leaving this row only in-house specs; (c) both hold on disjoint evidence. This must be decided once, on both rows, and cannot be left to whichever row lands second.
3. **NJ-MS-3** — if R1c ratifies the engineering keys, does this row need a `specification_id` concept distinct from `design_item`, or should `design_item` be widened to admit a specified object that is not a design item? This row proposes no key and will not pre-empt NJ-ENG-1.
4. **NJ-MS-4** — may supersession ever be represented as a fact, or must it remain an observation of what one document says about another? The safety argument favours observation-only; the retrieval argument favours a fact.
5. **NJ-MS-5** — recommendation to R1c, not a change made here: the engineering schema's `work_types[]` contains `"material or component specification"`, which is the strongest argument against this row's existence. If this row is ratified, that overlap should be adjudicated explicitly — either the value stays and is understood to be the artifact-type name that this template organizes, or it is removed. R1c owns that file; this row does not touch it.

## Final recommendation

Keep `engineering.material-specification` as a placeholder template with no fields, no dimensions, no parent activation and no time-first hierarchy. Its licence to exist is that the engineering schema's default template returns the wrong answer on every one of its fixtures, and that its recommended order inverts the default rather than subsetting it. Discriminate on the relation of specified-object to acceptance-criterion to test-method with an explicit absence of lot identity and measured result, hold the four reciprocal boundaries at issuer role, specified object, measured-versus-criterion and normative-versus-transactional, and route everything unresolved to Review Later rather than guessing.
