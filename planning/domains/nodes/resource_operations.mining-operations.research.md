# R1b lab notes — `resource_operations.mining-operations`

Date: 2026-08-27  
Assignment: `kind: template` · `schema_id: resource_operations` · `launch: placeholder`  
Result: **keep narrowly** (`refuse_node: false`), field-less and dimension-less pending R1c.

## Verdict and strongest charge

This row survives as a **mine/quarry extraction-history template**, not as an industry label. Its
anchor is a labelled relation among an operator-held authority, an extraction site, pit/bench/shaft/
plant or working area, measured material output, and an operational or reporting period. The relation
appears in mine plans tied to operating records, production returns, weighbridge reconciliations,
grade-control workbooks, post-activity surveys, environmental returns and progressive restoration.

The strongest charge is that this is merely a mineral value set inside the broad
`resource_operations` schema. That charge is real: the parent proposes the same six possible keys
(`site`, `operating_authority`, `asset`, `output_stream`, `reporting_period`, `record_type`) and its
default already covers authorised source → operating unit → measured output → period. The row stays
only because its **recognition grammar and recommended emphasis differ**:

- the parent default is source/output-led and provisionally recommends
  `site → operating_authority → output_stream → reporting_period → record_type`;
- mining is extraction-site and working-area-led: `site/permit → asset or working area → output
  stream → reporting period → record type`, with authority optional once the site is known;
- its decisive files distinguish planned permission from actual extraction, reconcile source/pit to
  material movement, and tie grade, survey, environmental and restoration evidence to the same mine;
- exact locations, reserves, production, grade and infrastructure layouts make this a sharper privacy
  case than generic operations, although the catalogue still uses only `potentially_sensitive`.

If R1c decides the parent template's optional asset-led branch already captures these differences,
this row should be refused. That alternative is recorded as NJ-MINING-1; preserving a legacy id is
not evidence.

## Authority stack and method

Read before drafting:

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, including the ratified J-DEPTH requirement.
- The complete stamped output of `python3 planning/domains/dispatch/make_prompt.py resource_operations.mining-operations`.
- `planning/00-database-agent-product-design.md` (authoritative for product-design quotations) and
  `planning/01-product-design-structured.md` (locator only).
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md`,
  and `planning/domains/CONNECTION-EXAMPLES.md`.
- `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, `planning/domains/ROSTER.md`,
  `src/evidence_shape/vocabulary.py`, and the ratified `planning/overnight/council/DECISION-BRIEF.md`.
- The landed `resource_operations` schema and its oil/gas sibling, used for exact field proposals and
  house idiom, plus the launch-depth `identity.core-documents` exemplar for observation/fact and
  false-positive discipline.
- Existing neighbour material for `engineering`, `construction_property.site-survey`,
  `government.permit-licensing`, `government.environmental-regulation`,
  `business_operations.compliance-audit`, `business_operations.corporate-regulatory-filings`,
  `logistics.warehouse-ops`, and resource-operation siblings. No neighbour file was edited.

The stamped assignment still carries retired “gist” wording; J-DEPTH in the standing brief and
decision brief controls. The connection contract also overrides the stamped generic example:
template rows do not author `also_holds_with`, and every collision below uses only
`{domain, signal, provenance}`.

## External evidence used

These sources establish recurring real-world file names and structures. They do not license product
fields, jurisdiction-specific identifier patterns, detector thresholds, authenticity judgments,
grade cut-offs, legal conclusions, or handling classes.

- [GOV.UK Minerals guidance](https://www.gov.uk/guidance/minerals) describes mineral planning,
  continuous monitoring of extraction, and restoration/aftercare conditions. It names restoration,
  aftercare, overburden, soil handling and progressive reclamation as recurring operator/planner
  concerns.
- [Natural England planning and aftercare advice](https://www.gov.uk/government/publications/reclaim-minerals-extraction-and-landfill-sites-to-agriculture/planning-and-aftercare-advice-for-reclaiming-land-to-agricultural-use)
  names restoration plans, soil resources, proposed after-use, aftercare programmes, landform maps
  and water/habitat features. Those are file structures, not automatic facts.
- [British Columbia annual reporting for mines](https://www2.gov.bc.ca/gov/content/industry/mineral-exploration-mining/permitting/mine-permit-requirements/annual-reporting)
  names annual reclamation reports, as-built mine maps, spatial disturbance data, mine-plan updates,
  production tables, environmental protection, reclamation and closure programmes. It also makes
  the operator-versus-regulator submission boundary concrete.
- [British Columbia Sand & Gravel / Quarry Annual Summary form](https://www2.gov.bc.ca/gov/content/industry/mineral-exploration-mining/documents/permitting/sand_and_gravel-_quarry_annual_summary_of_work_and_reclamation_002.pdf)
  demonstrates a recurring quarry form with permit number, report year, production and reclamation
  fields. A form title is never enough to activate this template.
- [BLM mining and minerals bonding](https://www.blm.gov/programs/energy-and-minerals/mining-and-minerals/bonding)
  confirms that plans/notices of operations and reclamation obligations can be paired with a bond and
  operator principal. This supports the authority/obligation structure without making bond numbers
  fields or proving that a plan was performed.
- [BLM recording a mining claim or site](https://www.blm.gov/programs/energy-and-minerals/mining-and-minerals/locatable-minerals/mining-claims/recording)
  describes serialised claims, plans of operation, environmental review and reclamation guarantees.
  It is evidence that identifiers and environmental structures recur, not a detector catalogue.

The product-design citations in this memo are verbatim from `00` and were checked against the source:

Exact quote check: “A file can simultaneously be a syllabus, part of a particular course, created for a particular semester, related to a university, included in an application package, a member of a version family, and potentially sensitive. These are separate facts about the same file.”
Exact quote check: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

- `00`: “A file can simultaneously be a syllabus, part of a particular course, created for a
  particular semester, related to a university, included in an application package, a member of a
  version family, and potentially sensitive. These are separate facts about the same file.” Mining
  records likewise retain operating-site, authority, asset, output and period evidence independently;
  the template does not turn them into one permanent category or path.
- `00`: “The system may create new values when it sees a new course, project, company, university, or
  event, but it should not invent new fields automatically.” This is why the legacy mining concepts
  are not minted as private fields.
- `00`: “A session should never be treated as proof of topic.” This is retained verbatim in the
  never-alone list and applies to portal exports and download sessions.
- `00`: “For document and record domains, project, function, or subject usually comes before time
  because putting year first scatters related work across calendar folders.” This is the reason for
  the site/asset-led recommendation.

## Bottom-up file set

The JSON records fourteen concrete fixtures. Together they cover native text, spreadsheets, CAD/GIS,
image/OCR, email, archive manifests, sparse group members, a false-positive research paper and the
same-byte seams with engineering, construction survey, government, logistics, business compliance,
corporate filing, renewable generation and farming.

1. **`North-Quarry_Mine-Plan-and-Restoration-Conditions.pdf`** (`text_document`). Operator,
   authorised boundary, mineral permission, extraction method, production limits and restoration
   conditions are labelled. It is an authority/plan fixture, not proof that extraction started. The
   authority's issuer-side decision can also activate Government; no site or permit fact is copied
   from the file name alone.
2. **`North-Quarry_Pit-3_Monthly-Production-Return_2026-06.xlsx`** (`spreadsheet`). A labelled
   mine permission, pit, month and operator frame rows for run-of-mine feed, waste/overburden,
   saleable aggregate, stock and units, with submission status. Quantities do not prove physical
   accuracy, finance ownership or that the filename month is the reporting period.
3. **`Pit-3_Weighbridge-and-Haulage-Reconciliation_2026-06.csv`** (`spreadsheet`). Ticket, pit/face,
   vehicle, carrier, material, destination, time and gross/net weight reconcile extraction to dispatch.
   It is the mining/logistics collision fixture; a destination and truck number do not decide the
   operating source.
4. **`Pit-3_Bench-12_Grade-Control-Reconciliation_2026-06.xlsx`** (`spreadsheet`). Sample/block and
   bench roles join assay, ore/waste classification, model-versus-actual grade and disposition. An
   assay value is not automatically a reserve, research result or output fact.
5. **`North-Quarry_Pit-3_As-Built-Survey_2026-06.dwg`** (`design_creative`). A controlled drawing
   contains measured surfaces, coordinates, stockpile volumes and a mine-plan as-built reference.
   The same bytes can belong to engineering's controlled drawing package or construction site survey;
   actual operating context is required for this row.
6. **`North-Quarry_Blast-Log_Shot-12_2026-06-18.pdf`** (`text_document`). Labelled shot/bench/face,
   actual blast date, charge/holes, exclusion checks, status and post-blast survey distinguish an
   actual activity log from a planned blast schedule. A signed form does not prove safety or outcome.
7. **`M-2048_Quarterly-Discharge-and-Dust-Monitoring_Return_Q2-2026.xlsx`** (`spreadsheet`). Operator,
   permit, monitoring points, parameter, method, result, unit, limit/exceedance and corrective action
   make this operator-side mine compliance evidence. A regulator receipt or enforcement assessment
   would shift the competing role to Government environmental regulation.
8. **`North-Quarry_Annual-Reclamation-Report_2025.pdf`** (`text_document`). Annual mining and
   reclamation activity joins disturbed/restored areas, waste/overburden, monitoring and liability
   estimates, with maps and photos. It does not establish regulator acceptance or final closure.
9. **`North-Quarry_Permit-and-Production-Submission.zip`** (`archive`). The manifest exposes a
   permit, production return, weighbridge reconciliation, survey drawing, monitoring return and
   reclamation report. Member dates/functions remain separate; the archive is not unpacked to create
   facts, and opaque CAD/GIS members may remain unsupported.
10. **`RE Pit-3 June production return.eml`** (`email`). Native sender/recipient roles, a June-return
    subject and attachment names provide group context. The message cannot donate attachment
    quantities, site or acceptance status to itself.
11. **`IMG_9311_Quarry-Face.jpg`** (`image`). Genuine EXIF and an industrial quarry scene support a
    Photos capture reading, but no readable pit/site/permit identifier supports mining activation.
    It may join an accepted mine group without copying group facts; otherwise it falls through to
    One-Off Images.
12. **`Geological-Resource-Estimate_North-District_2026.pdf`** (`text_document`). Geological
    interpretation, resource classification, assay and maps are topical but lack operator production,
    permit-condition or actual-extraction structure. It is a research/reading false positive.
13. **`North-Quarry_Road-and-Drainage_Construction-Drawing_RevC.dwg`** (`design_creative`). A quarry
    address and haul-road/drainage earthworks appear in a revision-controlled civil drawing with no
    production or authority relation. It is engineering/construction evidence, not mining operations.
14. **`North-Quarry_Progressive-Rehabilitation-Closure-Plan.pdf`** (`text_document`). Mine phases,
    disturbed areas, soil/overburden handling, landform, aftercare and closure obligations are joined
    to permit conditions. A generic construction or landfill after-use plan with no extraction context
    is rejected.

## Node test — all three legs

### 1. Detection signals differ from the parent default

The parent accepts many authorised-source and measured-output worlds: utilities, oil/gas, renewable
generation, farming, forestry and fisheries. Mining needs a narrower **extraction-operation grammar**:

- a mine/quarry/pit/bench/shaft/plant role joined to a permission and actual extraction or measured
  material movement;
- source-to-output reconciliation with ore/waste/overburden, grade, stock and dispatch roles;
- survey and grade-control evidence tied to an as-built or production state, not a generic map or assay;
- operator monitoring and progressive restoration tied to an extraction permit condition;
- planned authority separated from actual work, and regulator receipt/assessment separated from the
  operator's submitted return.

Mining, quarry, ore, tonnage, grade or permit words alone are deliberately abstentions. A geology
paper, civil drawing, haulage ledger, public statistical table and regulator case are useful tests of
the narrower boundary.

### 2. Recommended dimensions differ from the parent default

The parent schema's provisional default is `site → operating_authority → output_stream →
reporting_period → record_type`. Subject to R1c, mining recommends `site/permit → asset or working
area → output_stream → reporting_period → record_type`, with authority optional when the site spans
several permissions. Pit/bench/shaft/plant history is the intelligible subject for production,
survey, grade and restoration work; output streams are often search evidence rather than permanent
branches. Time is not first. The cited `00` sentence is verbatim: “For document and record domains,
project, function, or subject usually comes before time because putting year first scatters related
work across calendar folders.”

No order is serialized because PR-6 leaves the resource schema's fields empty. Putting proposed keys
in `dimension_order` would silently make them legal; the JSON's order rationale is evidence for R1c,
not a frozen filesystem path.

### 3. Privacy rules differ from the parent default

The parent already marks operations potentially sensitive, but mine records can concentrate exact
resource locations, reserve/grade and production performance, infrastructure layouts, haulage routes,
environmental exceedances, restoration liabilities and security-relevant operating details. A public
annual report does not make a private survey, plan or production packet safe to expose. P7 owns the
handling and model-access decision; no handling class is invented here.

## Proposed fields — six exact-key secondings, zero inventions

`fields` remains empty. The six `proposed_fields` entries repeat the parent schema's keys exactly:

- `site` — mine, quarry, pit or authorised operating area; not Photos' capture `location`.
- `operating_authority` — operator-held permission/lease/tenement and conditions; not Government's
  issuer-side case and not the rejected `permit_reference` spelling.
- `asset` — pit, bench, extraction face, shaft, crusher, conveyor, stockpile or weighbridge; no
  mining-specific `pit_id`.
- `output_stream` — ore, aggregate, concentrate, overburden, waste or recovered material; no grade,
  tonnage or unit field.
- `reporting_period` — production month, extraction year, survey campaign or return period; not
  creation date or tax year.
- `record_type` — permit, production, haulage, grade, survey, blast, environmental or reclamation
  function; no `record_class` or `mining_record_type`.

The superseded `mining.ops` draft in `planning/domains/13-trades-property-logistics.md` proposed
`site_or_mine`, `permit_reference`, `operator`, `record_class`, `reporting_period`,
`volumes_or_tonnage`, and `environmental_obligation`. Those were examined and deliberately not copied:
`site_or_mine`, `permit_reference`, `record_class`, `volumes_or_tonnage` and `environmental_obligation`
are private or over-specific spellings; `operator` is a role that is not currently licensed by the
schema and would confuse holder, landowner, contractor and regulator. The parent exact keys are the
only proposals sent to R1c.

## Recognition, abstention and grouping

Deterministic recognition requires labelled role clusters: permission/holder/area/conditions; pit or
bench/asset plus actual extraction or output; production or haulage rows with source and destination;
grade/survey records with an operating relation; or environmental/restoration records tied to a mine
condition. Rules should inspect structure and labelled cells, not just filenames. An LLM is reserved
for ambiguous source/output tables, permit-versus-regulator role, survey-versus-engineering meaning,
assay-versus-operations meaning, restoration-versus-construction purpose, poor OCR and multilingual
forms. It may propose only parent-schema fields after citing extracted evidence.

The grouping firewall matters in this domain. A calendar reminder, email or field photograph may join
an accepted mine group after a production or permit anchor, but it cannot receive site, asset, output
or period facts by proximity. A portal export or scanning session is a weak clue only. The archive
manifest can propose packet membership while each member keeps its own evidence and record function.

## Collision and reciprocal boundaries

The JSON contains ten `collides_with` edges. Each names the same concrete fixture bytes, explains why
both directions are plausible, and states the reciprocal boundary. In brief:

- oil/gas shares the permit/production shape but differs by well/field/facility versus pit/bench/material;
- engineering and construction site survey share controlled drawings and measured surfaces but differ
  by operational mine state versus technical design or civil/property commission;
- Government permit/environmental records share permission, conditions and monitoring tables but differ
  by operator-side activity versus issuer-side assessment/enforcement;
- compliance audit and corporate regulatory filings share compliance/submission forms but differ by
  audit controls/statutory wrapper versus mine activity and source-to-output evidence;
- logistics shares weighbridge, vehicle, destination and weight columns but differs by custody/movement
  versus extraction source and mine production;
- renewable generation shares source-to-output returns but differs by generator/energy interval versus
  pit/bench/material;
- farm records share land, soil, after-use and annual-work language but differs by crop/holding season
  versus authorised extraction phases and mine closure.

No `also_holds_with` edge is authored because this is a template. Per-file `also_schema` records are
evidence of independent possible co-activation; R1c owns schema-level co-activation decisions. No
`related_to`, `why`, `domain_id`, `id`, `target` or other non-contract collision keys are used.

## Files considered and rejected from activation

- A standalone permit, planning decision or reclamation bond: authority words and identifiers are not
  actual extraction; retain as Independent Records unless an accepted operational group supplies the
  missing relation.
- A geological resource/reserve estimate or assay certificate: mineral and grade language is not an
  operator production or grade-control record without pit/bench/output context.
- A public mineral-market outlook or commodity price sheet: topic and commodity values do not establish
  a permitted source, operating asset or measured mine output; Reading Inbox is safer.
- A haulage invoice, delivery note or cargo ledger: destination, vehicle and tonnage do not establish
  extraction source; Logistics or Finance may own it.
- A civil road, drainage, earthworks or building drawing at a quarry address: engineering/construction
  structure wins unless the drawing explicitly records an operating mine as-built state.
- A regulator's environmental assessment, inspection or enforcement file: mine vocabulary and permit
  number do not make it operator-side; Government owns the issuer/assessment role.
- An ordinary quarry photograph, screenshot, scanner batch, calendar invite or email: capture/session
  context cannot activate mining or copy group facts.
- An unsupported CAD/GIS, assay binary or encrypted archive: index safely and defer; extension and
  archive membership cannot establish content or record function.

## Sensitivity and unresolved questions

This template is `potentially_sensitive` because exact mine locations, reserves, production/grade,
plant layouts, environmental results, restoration liabilities and operational vulnerabilities may be
present. It assigns no handling class. Protection and cloud/local policy remain P7 decisions, and
raw identifiers, coordinates and quantities remain local evidence rather than folder levels.

### NEEDS-JOSEPH

1. **NJ-MINING-1 — distinct row or parent option?** After R1c adjudicates the six shared keys, should
   the extraction-site/working-area grammar remain a template, or is it only a reusable branch of the
   parent resource_operations default? Both are defensible; do not silently collapse the row.
2. **NJ-MINING-2 — authority branch privacy.** May `operating_authority` become visible in a folder
   proposal for permits, tenements and reclamation bonds, or should authority stay search-only because
   concession and critical-infrastructure identifiers may disclose sensitive information?
3. **NJ-MINING-3 — operator and regulator copies.** When a mine return and regulator receipt share the
   same bytes, should the merge require an explicit template collision with Government and corporate
   filing while allowing independently evidenced roles, or should one role own the item after a margin
   decision? The current row keeps the seam visible.
4. **NJ-MINING-4 — jurisdictional catalogues.** Which one-jurisdiction permit, mine-plan, authority,
   material and report catalogues will R2/R4 inject? This row deliberately supplies no identifier
   patterns, thresholds or gazetteers.
5. **NJ-MINING-5 — opaque survey and assay formats.** Should CAD/GIS/assay binaries remain indexed-but-
   unreadable until an approved extractor exists, or is a dedicated local extractor planned? The row
   does not treat an extension as content evidence.

## Self-check

- Both assigned target paths were absent before writing and only those two paths were added.
- JSON parses with `python3 -m json.tool` (run after write); source types are members of the closed
  vocabulary; edge domains and residual names are roster/contract-valid.
- `fields` and `template.dimension_order` are empty under PR-6; proposed keys are exact parent-schema
  secondings; template-level `also_holds_with` is empty.
- All fourteen file examples split observations from legal facts, include abstentions and residuals,
  and include labelled, sparse, archive, image, email, false-positive and collision fixtures.
- Every collision object has exactly `domain`, `signal`, `provenance`; each signal names `SAME FIXTURE
  BYTES` and explains both directions.
- No field/path is asserted as a fact, no numeric threshold or confidence score is invented, and no
  handling class is assigned.
