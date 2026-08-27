# Forestry and woodland records — R1b research memo

## Scope and authority

This memo owns only `resource_operations.forestry-records`. The stamped assignment identifies it
as a `kind: template` on `schema_id: resource_operations`; `parent_id` is null and is browse-only.
The output is therefore a template applicability record, not a new schema. The anchor
`planning/domains/nodes/resource_operations.json` is a PR-6 placeholder with `fields: []` and a
proposed operational field set for R1c. This row does not copy those proposals: its JSON has
`fields: []`, `proposed_fields: []`, and `template.dimension_order: []`. The conditional forestry
order is documented for R1c in prose only.

The sources read before writing were:

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped output of
  `python3 planning/domains/dispatch/make_prompt.py resource_operations.forestry-records`;
- `planning/prompts/ALIGNMENT.md`, `planning/00-database-agent-product-design.md`,
  `planning/01-product-design-structured.md`, `planning/domains/_CONTRACT.md`, and
  `planning/domains/CONNECTION.md`;
- `planning/domains/roster.json` and `planning/domains/canonical_fields.json`;
- `src/evidence_shape/vocabulary.py` for the closed `SOURCE_TYPES` list;
- the resource_operations schema anchor and landed `identity.core-documents` exemplar, plus
  landed resource_operations siblings for the JSON idiom and collision form.

The design does not name forestry as a separate schema or template. This is consequently a
proposal extending the named resource-operations situation. The exact design language that
controls this work includes:

- “Every file will be treated as a record with many facts, rather than forcing it into one
  permanent category.”
- “The engine should treat the file extension as a routing signal rather than an assumption about
  meaning,”
- “Archives should be inspected without being unpacked to disk.”
- “For document and record domains, project, function, or subject usually comes before time
  because putting year first scatters related work across calendar folders.”
- “A session should never be treated as proof of topic, and it should not carry the same confidence
  as a hash match or a directly extracted document fact.”
- “Independent Records may live under Personal/Independent Records and hold standalone
  certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader
  group.”
- “Review Later may hold files whose meaning is partly understood but whose final location
  requires a future decision.”
- “Protected Records may represent sensitive isolated material such as passport scans, medical
  documents, account statements, visas, legal forms, or credentials; it should normally remain
  local-only and must not cause filenames or content to be exposed in model prompts.”

Those quotations were checked against `00-database-agent-product-design.md`. The forestry-specific
file structures, context vocabulary and boundaries below are inferences from the named schema and
ordinary operational record forms, not claims that `00` itself names a forestry catalogue.

## Node test

The row is retained, provisionally, because all three legs differ from the schema anchor's default.

**Detection signals.** The anchor accepts a broad relation among an authorized source or site,
authority, asset or operating unit, measured output or environmental performance, and period.
Forestry requires the narrower managed-woodland relation: an estate or woodland is subdivided into
compartments, stands or coupes; a management plan, inventory, felling permission, harvest return,
sale reconciliation or restocking record connects that unit to a treatment, measured timber output,
condition or obligation. The same terms appear in public-land policy, property surveys, logistics,
engineering drawings and ecological research. The relation, not the word “forest”, is the signal.

**Dimensions.** The anchor's provisional schema order is `site -> operating_authority ->
output_stream -> reporting_period -> record_type`, with an asset-led alternative. Forestry is
normally compartment-led: `site/estate -> asset/compartment -> record_type`, with
`reporting_period` below recurring inventory, harvest and monitoring series and
`operating_authority` only where multiple licences, tenures or obligations divide the estate.
`output_stream` values such as sawlog, pulpwood, fuelwood or biomass are usually leaf values, not
standing levels. Because the schema remains field-empty at launch, the JSON serializes no order;
R1c must decide whether the proposed `asset`, `site`, `operating_authority`, `reporting_period` and
`record_type` keys are globally licensed.

**Privacy.** This situation adds concentrated exposure beyond generic resource operations:
precise boundaries, harvest windows, access routes, timber reserves, buyer prices, contractor
details and protected-habitat observations can reveal commercial plans, security-relevant access,
or ecological locations. `sensitivity` is therefore `potentially_sensitive`; no handling class is
invented, and no raw location, quantity, person, price or habitat fact becomes a dimension.

The strongest refusal charge is that forestry could be only a `work_type` value under the anchor,
which already mentions farms, forests, compartments, harvest and environmental records. The row
survives only when a corpus has the long-lived estate-to-compartment chain: prescription and
inventory precede felling, measured extraction feeds sale or settlement, and restocking and habitat
obligations continue after the cut. A lone timber invoice, generic land map, public forest report
or ecological paper does not satisfy this test and falls to the anchor or a residual.

## Bottom-up file set

Each example is a concrete file a land manager, forestry operator, contractor or small estate team
could retain. The JSON deliberately separates raw observations from facts. Since the anchor's
fields are deferred, `facts_legal` records universal facts available at launch; proposed resource
fields are named in `must_not_conclude` until R1c adjudicates them. `group_without_copying_facts`
means a sparse member can join an accepted estate or compartment group without inheriting its
labels.

### Management, authority and inventory

* `Northwood-Estate_Management-Plan_2026-2045.pdf` (`text_document`, `.pdf`): the title,
  contents and tables identify a woodland management plan, estate compartments, species or age
  classes, prescribed treatments and review periods; maps show access and conservation constraints.
  A plan supports a forestry candidate when its management-unit relation is clear, but it does not
  prove that felling is occurring now. It is not enough to infer a site or period from the filename.

* `Northwood-Compartment-Register_2026.xlsx` (`spreadsheet`, `.xlsx`): sheet headers label
  compartment, stand, area, species mix, age class, treatment and next review, with a summary sheet
  and detail rows. This is strong structured evidence of a management-unit register. Standing stock
  is not harvested output, and a workbook's year is not automatically the operational period.

* `C12_PreHarvest-Inventory_2026.csv` (`spreadsheet`, `.csv`): headers identify compartment C12,
  plot, species, diameter class, height and volume estimate, with survey date and plot identifiers.
  The rows distinguish standing stock from planned removal. A compartment code alone does not prove
  a felling licence or a sale; this member may join the accepted C12 group without copying estate
  facts onto it.

* `Felling-Licence_FL-2026-017_Coupe-C12.pdf` (`text_document`, `.pdf`): a labelled instrument
  names holder, issuing authority, coupe C12, permitted operation, conditions and effective dates;
  a schedule limits species and volume. This is an operator-side candidate only when joined to an
  estate/compartment activity packet. The same bytes can activate `government.permit-licensing`
  for the issuer's application, assessment and decision record; letterhead and licence number do
  not decide custody.

### Harvest, sale and restoration

* `C12_Harvest-Return_July-2026.xlsx` (`spreadsheet`, `.xlsx`): a return labels compartment,
  felling dates, product class, measured load volume, destination and reporting period; declaration
  fields identify the operator and rows reconcile sawlog, pulpwood and residue. The destination yard
  is not the forest site, and a declaration is not by itself a government-side receipt.

* `C12_Timber-Sale-and-Scale-Reconciliation.pdf` (`text_document`, `.pdf`): a schedule identifies
  harvested coupe C12, purchaser, scale tickets, timber grades and settlement lines; measured loads
  reconcile to the harvest return, and prices and payment terms are present. The operational
  extraction relation supports forestry; payment and account details may independently support
  Finance, while purchaser tender or award evidence belongs to procurement.

* `C12_Restocking-and-Regeneration-Return_2027.xlsx` (`spreadsheet`, `.xlsx`): the sheet labels
  harvested compartment, planting area, species, planting date, inspection, survival and remedial
  treatment, and references the prior felling authorization. A species is not an output-stream fact
  without this management relation, and a planting invoice is a false positive.

* `Northwood-Biodiversity-Monitoring_Compartment-C12_2026.pdf` (`text_document`, `.pdf`): sampling
  points and habitat features are tied to C12 and a licence condition; tables identify date,
  indicator species, method and result; the conclusion records action and follow-up. Operator
  monitoring supports this row. A regulator's receipt, officer review or enforcement action would
  support `government.environmental-regulation` instead or as independent coactivation.

### Maps, schedules, mail, OCR and archives

* `Northwood-Coupe-Boundaries-and-Haul-Routes.geojson` (`opaque_binary`, `.geojson`): structured
  feature properties label estate, compartment and haul-route identifiers, while geometry contains
  boundaries and tracks. Geometry alone does not establish active felling, a legal boundary or an
  operating authority. It can join an accepted estate group without writing those facts onto the
  map file.

* `Felling-Window-and-Inspection.ics` (`calendar`, `.ics`): the event title proposes a felling-window
  inspection, with location, organizer and attendees but no attached licence, register or measured
  operation. Calendar source type and a suggestive title are never-alone evidence; at most this is a
  sparse group member after a separate estate anchor is accepted.

* `Re_Felling-Licence-Condition-Query.eml` (`email`, `.eml`): sender and recipient roles identify an
  operator and authority contact; the body discusses a licence condition, inspection and proposed
  compartment visit. A proposed visit is not proof that a harvest occurred. Mail addresses and
  content are potentially sensitive and should not be exposed in general summaries without policy.

* `Scanned-Coupe-C12-Felling-Condition.pdf` (`ocr`, `.pdf`): OCR recovers partial headings for the
  coupe, licence condition, retained habitat and replanting, with handwritten inspection marks but
  unreadable identifiers and dates. OCR is possible evidence; it cannot turn unreadable values into
  direct facts or establish the authority role.

* `Northwood-Forestry-Records.zip` (`archive`, `.zip`): the manifest lists a management plan,
  compartment register, licence, harvest return, scale sheets and restocking report across several
  compartments and periods. The archive is not unpacked. No one compartment or period should be
  copied to the archive as a whole; member-level facts remain separately evidenced.

* `IMG_8172.jpg` (`image`, `.jpg`): camera EXIF and capture time are present, and the frame shows a
  forest track and felled logs, but no readable compartment, licence or scale identifier appears.
  Scene appearance and EXIF support Photos observations, not forestry activation. Missing EXIF would
  not prove a screenshot or an operational image.

The set covers labelled forms and unlabelled prose, native text, spreadsheet and structured-data
routes, OCR, image, email, calendar, archive and a collision fixture. There is no legitimate
forestry use for a contact export in this row; `.vcf` remains a privacy-protected contact format,
not an operational record. A presentation or audio/video field briefing could be a group member,
but neither source type alone activates the template.

## Recognition and abstention

The deterministic signals in the JSON are structural clusters, not keyword triggers. They require
some combination of labelled estate/woodland, compartment/stand/coupe, treatment or authority,
measured timber/output or ecological result, and an operational period. A GIS manifest can help only
when it joins the geometry to management or harvest evidence. The archive rule is manifest-only, as
the design requires archives to be inspected without extraction.

The `needs_llm` list is intentionally bounded and late: ambiguous prose, weak maps, unclear
spreadsheet roles, mixed archives and OCR-poor relationships need interpretation after deterministic
evidence, not an open-ended forest-topic classifier. The model must cite its packet and may return
unknown. It cannot infer a forest site from a neighbouring file, upgrade a session clue to a fact,
or choose a destination path.

The `never_alone` list blocks the principal false positives: forest/timber/felling words, permit
numbers, species and quantities, place names, maps, contractor names, source types, parent folders,
download sessions and absent EXIF. In particular, `Harvest-2026.xlsx`, `Timber Invoice.pdf`, a
forest-road drawing, a park boundary image and a calendar event are all plausible-looking files that
remain unresolved without the relation that distinguishes this template.

## Conditional dimensions and field restraint

The anchor's proposed keys are not legal launch fields, so this template adds no key. If R1c
licenses them, the recommended projection is:

`site/estate -> asset/compartment -> record_type`,

with `reporting_period` beneath recurring inventory, harvest and monitoring series, and
`operating_authority` only where licences or tenure instruments genuinely separate branches. This
is a recommendation, not a path. The user can reverse, remove or flatten it after seeing accepted
groups. `output_stream` should generally remain a value below the operational record rather than a
folder level: sawlog, pulpwood and residue are categories inside the harvest return, while the
compartment is the durable retrieval anchor. A year-first layout would split the same compartment's
plan, felling, harvest and regeneration history.

No new `forestry_record_type`, `species`, `compartment_name`, `felling_period` or `timber_grade`
field is proposed. These are values or observations, and inventing local spellings would violate the
global field vocabulary. `asset` is a candidate only because the schema anchor already proposes it;
R1c must decide whether a compartment can safely share that neutral operating-unit role with wells,
meters and farm blocks. The same applies to `site`, `operating_authority`, `reporting_period` and
`record_type`.

## Reciprocal boundaries and collisions

The JSON authors eight template-to-template `collides_with` edges. Every edge is exactly an object
with `{domain, signal, provenance}`; no bare strings, `domain_id`, `id`, `target` or `why` keys are
used. Every signal states both directions and names `SAME FIXTURE BYTES:` followed by one concrete
file. The edges are `provenance: inference` because `00` does not name these forestry neighbours.
Reciprocity is an R1c merge obligation: the neighbour rows must name this id or the pair must be
removed after evidence review.

1. **Engineering civil/structural.** `Northwood-Forest-Road-Culvert-Design-and-Harvest-Access.pdf`
   separates structural alignment, calculations, revisions and as-built acceptance (engineering)
   from an operating coupe's haul use, measured harvest and access obligation (forestry).
2. **Engineering commissioning/handover.** `Northwood-Harvester-Handover-and-First-Coupe-Run.pdf`
   separates acceptance tests, installed-instance reconciliation and transfer signatures
   (engineering) from first-coupe production and compartment reconciliation (forestry).
3. **Government permit/licensing.** `Felling-Licence_FL-2026-017_Coupe-C12.pdf` separates
   authority intake, assessment, decision, register and renewal (government) from the holder-side
   permission joined to an active estate, harvest return or restocking obligation (forestry).
4. **Government parks/public lands.** `Public-Forest-C12-Management-and-Access-Plan.pdf`
   separates public-estate stewardship, access policy and conservation programme (government) from
   the operator's compartment treatment, harvest and replanting schedule (forestry).
5. **Government environmental regulation.** `Northwood-Annual-Forest-Condition-Return_2026.xlsx`
   separates authority receipt, officer review, inspection and enforcement (government) from
   operator compartment observations, declaration and management action (forestry).
6. **Business corporate regulatory filings.** `Northwood-Forest-Annual-Return-and-Submission.xlsx`
   separates filing obligation, deadline, declaration, reference, acknowledgement and penalty trail
   (business operations) from inventory, harvest and environmental content (forestry).
7. **Business procurement/sourcing.** `C12-Timber-Harvest-Tender-and-Scale-Schedule.pdf`
   separates tender, supplier comparison, bid evaluation and award controls (procurement) from
   measured coupe output and scale reconciliation (forestry).
8. **Business contract administration.** `Northwood-C12-Harvesting-Agreement-and-Performance-Pack.pdf`
   separates clause tracking, notices, variations, insurance, payment certification and disputes
   (contract administration) from compartment harvest measurements and regeneration performance
   (forestry).

These are evidence-item mutexes, not claims that the domains are unrelated. The same fixture can
contain disjoint sections with different valid schema evidence; the collision signal says which
section wins when one item is ambiguous. No `also_holds_with` is authored because this is a template,
and CONNECTION restricts that edge to schema-to-schema relations.

## Intended coactivation for R1c (not authored as an edge)

R1c should consider coactivation where the same file genuinely carries independent evidence:

- the felling licence may carry the holder's operating permission and the authority's licensing case;
- the biodiversity return may carry operator monitoring and a regulator receipt or enforcement step;
- the timber-sale reconciliation may carry forestry harvest output, Finance account/record evidence,
  and a procurement or contract workflow;
- a public-forest plan may carry an operator compartment schedule and public-land stewardship facts;
- a camera image of a marked compartment may carry Photos capture facts while joining the forestry
  group only through accepted anchors.

The group relation must not copy estate, compartment, authority or period facts onto sparse members.
This memo records the intended coactivation for R1c; the JSON correctly leaves
`also_holds_with: []`.

## Neighbours considered but not edged

`business_operations.project-delivery` was considered for forestry-road and harvesting projects, but
the sharper competition is civil/structural engineering for the same road fixture and procurement
or contract administration for the commercial workflow. A generic project plan does not confuse the
operational forest relation by itself.

`business_operations.budget-forecast` was considered because timber forecasts and harvest budgets
contain volume and price. It is not a collision unless the same bytes combine forward assumptions and
approval/variance structure with an actual compartment return; the operational-versus-plan boundary
is already stated in the never-alone rules and can be added by R1c if a fixture is found.

`government.planning-application` was considered for woodland access roads and land-use proposals,
but the same-file boundary is better captured by civil/structural engineering and permit licensing:
a planning application is an authority-side development case, while this row needs an active managed
estate and operational records.

`government.public-records-foi` and `government.archives-recordkeeping` may store copies of forest
documents, but a government custody or public-disclosure wrapper is not the forestry operational
relation. `government.parks-public-lands` is the sharper public-estate collision.

`logistics` is a real neighbouring schema in the roster. A timber load, vessel, haulage or
origin-destination ledger is logistics when custody and movement are central; it is forestry when
the same bytes reconcile extraction from a named compartment to output and restocking. No edge is
authored here because the roster's generic logistics row is not a landed same-kind target in this
pass; R1c should revisit it if a concrete reciprocal fixture is available.

`construction_property` was considered for woodland roads, land access and surveys. A property/site
instruction or bounded works contract is construction/property; a recurring compartment-to-harvest
record is forestry. The civil/structural edge captures the most concrete same-file confusion without
turning every land file into a collision.

`finance` was considered for timber settlements and buyer payments. A sale reconciliation can
coactivate Finance on its account and transaction evidence, but price or payment alone is not a
forestry collision. The intended coactivation is recorded above rather than as template
`also_holds_with`.

`photos` was considered for field images and aerial imagery. Capture location, camera and event are
separate Photos facts; an isolated woodland image falls through to One-Off Images, while an image
that documents a known compartment can join the forestry group without copying the compartment fact.

## Residual routing and safety

The JSON routes five residual cases. A detached licence, plan, certificate or notice with durable
purpose goes to Independent Records. A readable map, spreadsheet, email, OCR scan or archive with an
unsettled role goes to Review Later. An encrypted GIS/database package or damaged scan goes to
Unsupported or Encrypted. An unassociated woodland photograph goes to One-Off Images. Timber
contracts, exact boundaries, harvest plans, account-bearing settlements and habitat-sensitive
observations may go to Protected Records when no safe accepted group exists. Residual routing is not
a new forestry domain and does not make a file's category permanent.

## Proposed fields, refusal and NEEDS-JOSEPH

`proposed_fields` is intentionally empty. The template uses no private field names and does not
repeat the resource_operations anchor's deferred proposals.

The row is not refused, but its status is conditional. R1c should refuse it if real corpora show
only generic timber invoices, isolated permits, public forest reports or images with no repeating
estate/compartment-to-operation chain. In that event the anchor and residuals cover the evidence;
there is no need to preserve an industry label.

NEEDS-JOSEPH items for this node:

- **NJ-FOREST-1:** Should `asset` be the shared neutral operating-unit key for compartments, farm
  blocks, vessels, wells and meters, or should a compartment remain unresolved until a more specific
  global field is approved? A private `compartment` key is not minted here.
- **NJ-FOREST-2:** Should `operating_authority` be destination-eligible for felling licences and
  public-land tenure, given the retrieval value against disclosure of concession identifiers,
  boundaries and protected habitat?
- **NJ-FOREST-3:** When one timber packet contains measured harvest, purchaser contract and payment
  records, should forestry, Finance and business-operation schemas coactivate independently with the
  same fixture bytes, or should user policy choose one group owner? The template cannot resolve that
  policy and therefore leaves `also_holds_with` empty.

## Self-verification

The two target paths were absent before writing and no other path was edited. The JSON parses with
`python3 -m json.tool`. Its key set follows the landed resource_operations template siblings;
`fields`, `proposed_fields`, `dimension_order` and `also_holds_with` are empty as required for this
placeholder template. Every `file_examples.source_type` and `file_kinds.source_types` member is in
the exact fourteen-member `SOURCE_TYPES` vocabulary. Every residual name is one of the nine named
residual homes. The eight collision domains are roster endpoints; each collision has exactly
`domain`, `signal`, `provenance`, each signal explains both directions and includes `SAME FIXTURE
BYTES`. No bare collision strings, numeric thresholds, handling classes, fabricated design
quotations, or unlicensed field rows were added.
