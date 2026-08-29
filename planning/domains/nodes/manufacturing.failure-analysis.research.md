# manufacturing.failure-analysis — lab notes (R1b)

Date: 2026-08-27  
Depth: J-DEPTH  
Roster row: `kind: template`, `schema_id: manufacturing`, `launch: placeholder`, `parent_id: null`.  
Output: [`manufacturing.failure-analysis.json`](manufacturing.failure-analysis.json).

## Sources actually used

### Binding local sources

- The stamped assignment from `planning/domains/dispatch/make_prompt.py manufacturing.failure-analysis` fixed the two output paths, template kind, fieldless manufacturing schema, three neighbour families and residuals.
- `planning/00-database-agent-product-design.md` is authoritative. It supplies the observation/fact separation, multi-domain facts, extractor coverage, prohibition on automatic field invention, placeholder status, graph non-propagation, authorship prohibition and residual behavior. Only its exact words appear inside quotation marks.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/CONNECTION.md`, `CONNECTION-EXAMPLES.md` and `_CONTRACT.md` supplied the node test, activation/grouping firewall, closed edge vocabulary, schema-only `also_holds_with`, browse-only parent and template-field rules.
- `planning/domains/roster.json`, `canonical_fields.json` and `src/evidence_shape/vocabulary.py` were checked mechanically. Every collision endpoint is a roster id, every residual is one of the nine allowed names, and every example source type belongs to `SOURCE_TYPES`.
- `planning/overnight/council/DECISION-BRIEF.md` supplied ratified J-IND and PR-6 context: this professional-world placeholder receives full research but writes no field rows.
- `finance.crypto-assets.research.md` supplied the landed J-DEPTH calibration. `identity.core-documents.json` supplied the required object-shaped edge idiom.
- Reciprocal sibling evidence was read directly from `manufacturing.maintenance-work-order.json`, `engineering.risk-analysis-fmea.json`, `engineering.verification-validation.json`, and `engineering.simulation-analysis.json`. This row uses their same fixture bytes and states both directions.

### External reality checks

These sources establish real investigation artifacts and methods. They do not license fields, patterns, thresholds or folder trees.

- NASA's materials-process report describes preserving failed hardware evidence before handling or dissection, diagnostic techniques, controlled reproduction specimens, and fault trees supported by analysis, testing and document review. That grounds the as-received record, teardown sequence, hypothesis matrix and reproduction-test examples.
- NASA's ISS fiber-optic root-cause report is a real investigation in which competing theories were tested against destructive physical analysis and experience, and a defect was reproduced. It grounds the distinction between a proposed explanation and a supported cause.
- NIST SP 960-16e3, *Fractography of Ceramics and Glasses*, establishes fractography, microscopy, fracture patterns and practical failure-analysis case work. It grounds the micrograph, specimen map and fracture-origin report without pretending that an image alone activates the row.
- NIST's pressure-vessel investigation account describes review of property data, micrographs, material standards, code documents and ultrasonic examinations, followed by fracture-mechanics analysis and a most-likely cause. It grounds heterogeneous evidence joined into one investigation.
- FAA AC 437.73-1 distinguishes root-cause analysis, elimination of causes not supported by data, fault-tree analysis, corrective/preventive actions and validation of those actions. It grounds the strict boundary between causal conclusion and CAPA closure.

## Node test — all three legs argued

**Detection differs.** The manufacturing anchor sees production and quality records. This row requires an occurred failure plus a causal argument: identified occurrence, preserved condition, competing hypotheses, tests or examinations, rejected causes and a supported conclusion. Neither a failed inspection nor a failure-code line is sufficient. The happened-versus-hypothesised distinction also separates it from FMEA.

**Recommended dimensions differ.** PR-6 prevents serialising dimensions, but the R1c recommendation is affected product or asset, then `quality_event`. Record-type-first would split photographs, teardown, spreadsheets, correspondence and the final report into separate branches even though one investigation is the unit. Cause-first is worse: cause is a revisable conclusion, not a stable parent. Year-first scatters repeat investigations of one item.

**Privacy differs.** The investigation aggregates proprietary design details, supplier and customer data, employee statements, failure images and potentially safety-relevant incident facts. Unlike a routine manufacturing execution record, it often joins the most sensitive material from several systems. The row therefore stays `potentially_sensitive` while leaving handling entirely to P7.

The row survives. Its organizing situation is not a document type or work-type value; it is an evidence-preserving causal case spanning heterogeneous files.

## Bottom-up corpus and collision fixture

Eleven concrete examples cover labelled reports, an occurrence-bound 8D, repeated-event analysis, mixed archive, sparse microscopy image, hypothesis workbook, verification package, simulation, email, work-order false positive and prospective-FMEA false positive.

The sharp collision is `CNC-07 spindle - repeated bearing failures.pdf`. Maintenance and failure analysis see the same asset and work-order identifiers. Maintenance owns an individual dispatched job and its closure. Failure analysis owns several events assembled into a causal argument. The discriminating bytes are hypotheses, evidence, rejected causes and conclusion; a free-text suspected-cause line never transfers the completion report.

Three other reciprocal seams use exactly the fixtures already authored from the opposite side:

- `8D_Report_Field-Return-4471.pdf`: occurred failure versus prospective FMEA.
- `DVT-07_Test-Package.zip`: criterion failure versus investigation of why.
- `FA4471_fracture-reproduction_FEA_RevB.pdf`: physical causal case versus computational study.

The CAPA seam is also explicit: disposition/action closure and causal support are different claims even when one controlled package contains both.

## Files considered and rejected

- A single repair completion report with a failure code and suspected-cause sentence: maintenance evidence, not a causal case.
- A standalone nonconformance or rejected inspection sheet: proves an output missed a requirement, not why.
- A DFMEA/PFMEA: prospective ranked failure modes tied to a revision, with no occurred-event anchor.
- A CAPA action tracker: may own containment, responsibility, due dates and effectiveness closure without technical cause evidence.
- A warranty returns ledger: a population of complaints until it actually argues a common mechanism.
- A microscope image whose filename says fracture origin: interpretation in a filename is not specimen identity or a supported conclusion.
- A CAD model of the failed part: as-designed definition, not occurred-failure evidence.
- A maintenance manual or troubleshooting guide: generic procedure for a type, not an investigation of one occurrence.
- A purchase return authorisation or credit memo: logistics/receipt evidence despite the word defective.
- A safety incident report: may trigger a technical investigation, but incident sequence and regulatory reporting are not automatically materials failure analysis.

## Fields and dimensions

`fields` is exactly empty. The template cannot copy a schema's fields, and manufacturing is a PR-6 placeholder with none declared.

`proposed_fields` contains one reused anchor proposal: `quality_event`. No failure-specific synonym was minted. It is needed because one investigation can bind several work orders, samples, tests and an affected article; none of those identifies the causal case. Its final scope is unresolved, so `dimension_order` remains empty.

The proposed R1c order is affected product/asset → quality event. Investigation authors, analysts, suppliers and customers are never destination dimensions. A root cause is also not a dimension because it is a revisable conclusion.

## Neighbours considered without an edge

- `logistics` was required by the assignment. A return-merchandise authorisation and shipping damage claim can trigger an investigation, but the logistics artifact proves custody or movement, not cause. No same discriminating evidence justified a collision beyond filenames and references.
- `business_operations` was required. Incident/problem-management records can use root-cause vocabulary, but their object is service or process restoration rather than a physical article. The current roster evidence did not supply a stable same-fixture reciprocal boundary, so no speculative edge was written.
- `manufacturing.inspection-record` was considered. A rejected characteristic triggers the case but remains conformity evidence. `engineering.verification-validation` already captures the sharper criterion-failed seam without giving one evidence item three homes.
- `manufacturing.quality-management-system` was considered. A QMS procedure defines how investigations are performed; an executed case applies it. Shared templates and citations are not the same bytes.
- `research.lab-notebook-protocols` was considered. A materials lab may generate both, but a general knowledge-producing protocol is not occurrence-bound.
- Identity, medical and legal schemas were not asserted merely because names, injuries or claims can appear. Those facts require independent evidence and schema activation.

## `also_holds_with` and salvage

`also_holds_with` is empty deliberately. The assignment clarified that it is schema-to-schema record-template intent for R1c, not a template edge. Mixed packages are represented through file examples and grouping; no illegal bare string or template-to-template edge was authored.

There was no salvage draft: neither owned file existed at dispatch time, so this row was created without overwriting live work.

## NEEDS-JOSEPH

- **NJ-MFG-FA-1 — scope of `quality_event`.** Should one broad case handle join failure analysis, nonconformance, complaint and CAPA, or should an investigation identifier remain distinct from the initiating event? One key makes cross-record joins easy but can collapse independently numbered records. Several keys preserve fidelity but risk rebuilding the private-vocabulary failure. Until R1c decides, this row serialises no dimension order and creates no failure-specific key.

## Verification performed

- JSON parsed with `python3 -m json.tool`.
- Exact key set compared with landed J-DEPTH template rows; template fields remain empty.
- Every `collides_with` item has exact `{domain, signal, provenance}` shape and every signal says `SAME FIXTURE BOTH SIDES` while assigning both directions.
- Every collision endpoint resolves in `roster.json`; every residual target is allowed.
- Every `file_examples.source_type` is in `SOURCE_TYPES`.
- Every quotation attributed to `00` was matched back to `planning/00-database-agent-product-design.md`; external claims are paraphrases, not quotations.
- No thresholds, scores or handling classes were introduced.
- Only the two assigned files were written.
