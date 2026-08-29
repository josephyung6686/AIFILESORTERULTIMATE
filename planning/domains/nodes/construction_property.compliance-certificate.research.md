# construction_property.compliance-certificate — research memo

**Depth: J-DEPTH.** Deepened from the retired gist draft on 2026-08-25. Row
`construction_property.compliance-certificate`; kind `template`; schema `construction_property`;
launch `placeholder`; absorbs and retires legacy `trade.compliance-certificate`.

**Verdict: REFUSED, preserved and strengthened.** The old draft was right: *certificate* names a
document genre, while the roster hint's need to produce the document years later names a retention
purpose. Neither is an organisational situation. Deepening found more routes for the bytes, not a
reason to resurrect the row.

## Sources actually used

### Binding sources

- `planning/00-database-agent-product-design.md`, the only source quoted below. The decisive exact
  sentence is: “Independent Records may live under Personal/Independent Records and hold standalone
  certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader
  group.” The extraction guardrails used in the JSON are “treat the file extension as a routing
  signal rather than an assumption about meaning” and “The graph does not automatically copy those
  missing facts onto sparse files.” The abstention rule is “Correct abstention is a successful
  outcome because the product’s goal is reliable organization, not maximum file movement.”
- `planning/domains/CONNECTION.md` — node test, activation ordering, closed edge vocabulary,
  reciprocal boundaries, and the failures created by work types posing as nodes or residuals posing
  as domain templates.
- `planning/domains/_CONTRACT.md` — especially the placeholder-field prohibition, the rule that a
  dimension may branch only on a declared field, and the closed top-level key set.
- `planning/prompts/ALIGNMENT.md`, `planning/01-product-design-structured.md`,
  `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, `ROSTER.md` Appendix A,
  `planning/overnight/council/DECISION-BRIEF.md`, and `src/evidence_shape/vocabulary.py`.

### Anchor and neighbours read before editing

- `construction_property.research.md` — the deepened family anchor. It defines this world as an
  occupation around an instructed property, makes documentary structure rather than building
  vocabulary the family discriminator, and states the default recommendation as property/site →
  instruction → document function, not time-first. It expressly identifies `certificate` as a
  `work_type` value and endorses this refusal.
- `construction_property.building-control`, `construction-project`, `trade-job`,
  `block-management`, `tenancy-management`, `agency-listing`, `site-health-safety`, and
  `materials-delivery`, JSON and memos where landed. These are the construction/property situations
  that actually own certificate-shaped files.
- `business_operations.corporate-regulatory-filings` — registry certificates survive there because
  the situation is the compelled submission round trip, not because the output says certificate.
- `finance.household-property`, plus the relevant finance insurance posture — a householder's own
  completion/compliance certificate and a latent-defects policy are not professional construction
  instructions merely because they concern a building.
- Every landed node file that cites this refusal was found with `rg`. Those citations consistently
  treat it as the negative control for document-type rows. In particular, `materials-delivery`
  distinguishes its two-address/two-quantity relationship from this row's label-plus-address failure,
  and `site-health-safety` distinguishes a recurring next-due inspection cycle from a certificate.
  This pass preserves those readings.

No external catalogue is consumed. Scheme names and standards are observations; no gazetteer,
regex, threshold, legal-validity test, or compliance judgement is proposed.

## What the label covers, and why that breadth is the problem

The legacy label collects outputs that share a title but not a filing situation:

- an installer's signed electrical declaration at the end of a trade job;
- a commissioning certificate in a construction handover pack;
- an authority's completion certificate closing a building-control application;
- a gas-safety record in a landlord/tenant compliance cycle;
- an EPC assembled for a sale or letting;
- a lift examination with a next-due date in a site-safety or block-management cycle;
- a declaration of performance travelling with a delivered batch;
- a structural warranty that is an insurance contract;
- a corporate registry certificate with no property at all; and
- a personal competence certificate or licence.

The same noun crosses installer, regulator, landlord, seller, manufacturer, insurer, registrar, and
individual-credential situations. Conversely, one job handover group contains certificates,
warranties, test sheets, drawings, manuals, photographs, and correspondence. The genre cuts across
the useful groups instead of defining one. That is precisely why it must remain a `work_type` value.

The certified-declaration structure is nevertheless real: labelled premises or asset, named scheme
or standard, issuer identity or registration, signed declaration, issue date, and sometimes test
results. It can support the **schema** being plausible. It cannot decide which **template** owns the
file. A detector that recognises the form still needs the application reference, accepted job,
delivery event, tenancy, block, sale/letting instruction, policy apparatus, filing round trip, or
credential holder to route it.

## Node test, all three legs

CONNECTION's template test asks whether detection signals, recommended dimensions, or privacy rules
differ from the schema default. One genuine difference would suffice. None exists here.

### Leg 1 — detection signals: fails

The strongest candidate is the certified-declaration structure just described. It answers “what
kind of document is this?” It does not answer “what organisational situation produced or keeps it?”
The exact same structure appears in a one-off domestic electrical record, a subcontract handover, a
condition-discharge submission, a managed-building register, and a delivery's product-conformity
pack.

Strip away the form layout and the remaining tokens are weaker still:

- `certificate`, `declaration`, `approval`, `warranty`, `test record`, and `inspection report` are
  document-function words;
- a postal address may be site, insured premises, landlord property, correspondence address, or
  merely the subject of a report;
- a contractor, installer, scheme, manufacturer, authority, or assessor name has multiple roles;
- a standard number or registration number does not establish the holder's situation;
- an issue, expiry, or next-due date is meaningless without its labelled role; and
- an extension or source type is only a routing signal.

The family anchor's constitutional never-alone argument applies: a multi-role token cannot activate
a group by itself. Pairing several never-alone tokens can make the schema plausible, but it still
does not distinguish this proposed template from the situations around it. Authoring the structure
again here would make a refused node appear executable and would contradict the anchor that already
owns the schema-level structure.

The collision test makes the failure concrete. `Completion certificate.pdf` may be an authority
closure under an application reference or an installer's declaration under a job reference. The
filename, address, signature, and word *complies* can be identical. The discriminating bytes are the
authority/application apparatus versus the installer/job apparatus, and those bytes activate the
two surviving situations. Nothing activates a third “certificate situation.”

**Result: fails.**

### Leg 2 — recommended dimensions: fails

The JSON order is empty by contract because the placeholder schema declares no fields. Against the
anchor's prose recommendation, certificates want exactly the owning situation's order: property or
site, then instruction, then document function. A recurring block or safety cycle may add its period;
a one-job corpus may omit a meaningless one-child property level. Those are ordinary template
choices already made by the surviving owner, not a certificate-specific order.

Issue date first would scatter one handover pack across years and split a property's durable records
by incidental issue date. Issuer first would collect unrelated certificates under the same authority,
scheme, contractor, or manufacturer. Standard first would turn a regulatory vocabulary token into a
collector. Certificate type first would simply recreate the document-type row as a directory.

**Result: fails.**

### Leg 3 — privacy rules: fails

The material inherits the construction/property schema's `potentially_sensitive` posture: real
addresses, occupiers, tenants, engineers, signatures, asset identifiers, and sometimes security-
relevant installation detail. That is important, but not distinctive.

Where a file needs stronger treatment, the reason belongs to its owner: an injured person's medical
detail makes a site-safety record protective; tenant detail belongs to tenancy/block handling; an
insurance policy follows Finance ordering; a personal licence follows the credential situation.
Conversely, a public product declaration or public authority certificate may contain little private
material. The word *certificate* supplies no coherent extra privacy rule.

**Result: fails. Overall result: refuse.**

## Exhaustive route-by-owning-situation map

This map closes the escape route “the row is refused, therefore the file is stranded.” The route is
selected only after the destination situation has independent evidence; the certificate does not
copy that situation's facts onto itself.

| Certificate-shaped file | Owning situation | Discriminator |
|---|---|---|
| authority completion, final, approval, or condition-discharge certificate | `construction_property.building-control` | authority issuer plus application/condition reference and approval lifecycle |
| installer declaration, minor works, commissioning, test, warranty, or as-built certificate in a project handover | `construction_property.construction-project` | accepted project/job plus purpose-coherent handover pack |
| the same installer declaration in a small direct trade instruction | `construction_property.trade-job` | accepted trade job, customer/site, quote/work/order chain |
| manufacturer declaration of performance, batch conformity or product certificate travelling with goods | `construction_property.materials-delivery` | batch/consignment relation, deliver-to/invoice-to structure, receipt event |
| periodic plant examination, permit, inspection or next-due record | `construction_property.site-health-safety` | asset/site safety cycle and labelled next-due or issue/hand-back structure |
| recurring fire, lift, asbestos, water, door or communal-system evidence for a managed property | `construction_property.block-management` | managed block plus recurring compliance obligation |
| landlord gas/electrical record issued to or for an occupier | tenancy-management situation | landlord/tenant roles and tenancy lifecycle |
| EPC, safety record, or warranty assembled for marketing a sale or letting | `construction_property.agency-listing` | accepted sale/letting instruction and marketing pack |
| household's own completion/compliance certificate or system warranty | `finance.household-property` | householder custody of their own property record, no professional instruction |
| structural warranty, latent-defects policy, or certificate of insurance | Finance insurance situation | policy number, insured party, coverage and premium/period apparatus |
| registry certificate of incorporation, good standing, registration, or filing acknowledgement | `business_operations.corporate-regulatory-filings` | compelled submission round trip, entity identifier, registry issuer/reference |
| licence, competence, course-completion, or professional registration certificate held for a person | relevant identity/career credential situation | named holder and credential/issuer/validity lifecycle, no property instruction |
| certificate with a real durable purpose and no accepted broader group | `Independent Records` | the residual definition applies literally |
| meaning partly understood but owning situation unresolved | `Review Later` | placement needs a future decision |
| sensitive isolated tenant, insurance, identity, or injury-bearing record | `Protected Records` | protection precedes ordinary placement |
| photographed paper with no event/project/reference family | `One-Off Images` | image capture is all that is established |
| disposable portal/status capture | `Temporary Screenshots` | screenshot purpose, not certificate genre |
| published technical certificate or declaration saved only for reading | `Reading Inbox` | reference material, no accepted site/delivery/job |
| unsupported or encrypted certificate file | `Unsupported or Encrypted` | content cannot be safely established |

`Receipts and Confirmations` was required by dispatch and considered carefully. It is appropriate for
a booking, purchase, submission, or portal acknowledgement whose purpose is confirmation of an
event. It is **not** the generic fallback for a durable compliance certificate: `00` names standalone
certificates under Independent Records. A filing receipt goes with the filing situation when that
situation is established; a bare transactional confirmation can use the residual. Thus both required
residuals are covered without conflating them.

## File fixtures and reciprocal boundaries

The JSON keeps eleven fixtures. Their purpose is not to demonstrate a hidden certificate group; each
demonstrates a distinct owner or abstention boundary.

### `construction_property.building-control`

Shared bytes: `Completion certificate.pdf`. This refused row must not take an authority-issued
closure merely because its title says certificate. Building control must not take an installer's
declaration merely because it mentions compliance and an address. Authority identity plus an
application or condition reference selects building control; installer registration plus accepted
job/handover evidence selects the job. With neither, Independent Records or Review Later.

### `construction_property.construction-project` and `trade-job`

Shared bytes: `Electrical Installation Certificate - 18 River Court.pdf` and
`Handover pack - Harbour Works.zip`. The job rows take the certificate only through an independently
accepted instruction or pack. They must not copy job, client, property, or contractor facts from a
neighbouring group onto a sparse certificate. This refusal must not pull one member out of the pack:
the pack is purpose-coherent and the job is the situation.

### `construction_property.materials-delivery`

Shared bytes: `DoP - steel batch 8841.pdf`. Materials delivery takes it when the batch token and
consignment evidence connect it to a physical arrival. It must not take the manufacturer's public
technical-library copy merely because product and standard match. This refused row takes neither;
the isolated published copy is reading material, while an isolated durable copy is Independent
Records. This agrees with the delivery memo's explicit reading of the same fixture.

### `construction_property.site-health-safety`

Shared bytes: `LOLER examination - Tower Crane 2 - next due 2026-10.pdf`. Site safety takes the
recurring asset/site inspection cycle and its labelled next-due slot. It must not take a one-off
domestic installation declaration with no site safety regime. This row cannot take either merely on
the noun certificate. Health or injury material receives protective ordering before placement.

### Block management, tenancy, sale/letting, and household property

Shared bytes: `Gas safety record 2026.pdf`, `EPC.pdf`, and
`Fire door inspection - Harbour Works - Q1.xlsx`. The same gas record can be a landlord obligation,
a managed-block record, or the householder's retained file. The EPC can be a marketing-pack member
or an isolated household record. The fire-door schedule belongs to the recurring managed-property
cycle, not to a certificate genre. Roles, custody, repetition, and an accepted instruction decide;
an address never does.

### Finance insurance

Shared bytes: `Structural warranty policy.pdf`. Finance takes the labelled policy apparatus. The
construction job may also hold a copy in handover, but it cannot erase the policy's Finance meaning;
protective ordering runs first. This refused row adds no third interpretation.

### Corporate regulatory filings

Shared bytes: `Certificate of incorporation - Harbour Works Ltd.pdf`. The registry seal, entity
number, effective date, and compelled filing round trip select corporate regulatory filings. A
company name containing a project or property word must not activate construction/property. In the
other direction, corporate filings must not take an authority's building completion certificate:
the regulated object is works under an application, not an entity filing.

### Photos

Shared bytes: `IMG_5510.jpg`. A photograph of a document does not create a new substantive situation.
OCR is evidence and may recover only fragments; it cannot promote a partial address or scheme name
to fact. If the underlying owner is established, the capture joins without copied facts. Otherwise
it remains a one-off image or temporary screenshot according to capture purpose.

## Files considered and rejected

These tempting false positives were deliberately not turned into extra JSON examples where the
existing fixtures already prove the boundary:

- a blank certificate template: form layout without a completed asset, issuer, declaration, or
  owning instruction; Reference Clips or Reading Inbox, not activation;
- a calibration certificate for a test instrument: equipment-maintenance or quality evidence when
  a real asset cycle exists, otherwise Independent Records; it does not certify the building;
- an asbestos register or fire-risk assessment: recurring risk-management evidence, not necessarily
  a certificate and not a one-off installer declaration;
- a completion statement from a conveyancer: finance/legal transaction apparatus, not authority
  approval of works;
- a certificate of insurance: policy evidence, not construction compliance;
- a certificate of incorporation or good standing: corporate registry evidence, even when the
  company name resembles a development;
- a training certificate, CSCS-style card, driving qualification, or examiner credential: a person's
  credential, not the installation they worked on;
- a certificate of analysis downloaded from a manufacturer's website: manufacturing/quality or
  reading material absent a specific received batch;
- a planning decision notice: authority decision in building control/planning, not an installer
  certificate;
- a warranty registration email: confirmation of an event; it can group with a job or policy but
  does not establish either by itself;
- `certificate.pdf` in an encrypted archive: Unsupported or Encrypted; filename semantics cannot
  overcome unreadable content; and
- a screenshot saying “certificate issued”: Temporary Screenshots or Receipts and Confirmations
  unless an independently accepted lifecycle exists.

These rejections matter because each shares vocabulary, address, issuer, or signature evidence with
the proposed row. None supplies a certificate-specific situation.

## Fields, work types, edges, and residual discipline

`fields: []` is binding for this placeholder. No canonical key is licensed through this row and no
proposal is needed: `proposed_fields: []`. Property, instruction, issuer, standard, registration,
certificate type, validity, and asset are tempting facets, but a refused template cannot become a
back door for a second schema. The surviving owner may argue its legal fields in R1c.

`work_types` records the certificate taxonomy as values and a routing aid, not as an activation enum.
It intentionally includes apparent near-neighbours — warranty, inspection, report, declaration,
licence — because the boundary problem is exactly that the title varies while the owner remains the
situation.

`collides_with`, `also_holds_with`, and `role_split` remain empty. A refused row cannot be a mutex or
coexisting destination; authoring edges would make R1c owe reciprocals to a node that never fires.
The reciprocal boundaries therefore live in this memo and on the surviving rows. Some files truly
also hold another schema — structural warranty/Finance, photographed certificate/Photos, authority
completion/Government, corporate certificate/Business Operations — and that coexistence is recorded
on fixtures without pretending this refused template is one of the coexisting schemas.

The residual list in JSON contains the five most direct output routes. The fuller route table also
names Reading Inbox, Receipts and Confirmations, Reference Clips, and Unsupported or Encrypted so
that no plausible certificate is stranded. Not every residual belongs in `falls_through_to`: the
JSON list stays focused on observed fixture routes, while this memo states the complete decision
surface.

## NEEDS-JOSEPH

**NJ-CP-CC-1 — ratify route-by-owning-situation at R1c.** Confirm the complete map above, especially
the seams newly made explicit in this pass: batch conformity → materials delivery; recurring
next-due inspection → site health/safety or block management; registry certificate → corporate
regulatory filings; personal competence certificate → credential situation. The cost of rejecting
the map is not a missing certificate: each unmatched durable file still has Independent Records.
The cost is only whether a recognised surrounding lifecycle may claim it.

If R1c overturns the refusal, the minimum honest alternative is a detection-signal-only template on
the certified-declaration structure. This memo recommends against that alternative because the same
structure identifies the construction/property schema across mutually different situations and is
already authored on the schema anchor. A live row would either never activate after its never-alone
guards, or steal files from the situations that provide the actual organisational context.

No other open question remains. There are no proposed fields, thresholds, statistics, handling
classes, or invented catalogue dependencies to adjudicate.

## What changed in this pass

Preserved: `refuse_node: true`; all three failing node-test legs; empty fields and proposed fields;
empty executable recognition; empty dimension order; schema-matching sensitivity; the eight original
fixtures; and the primary Independent Records route.

Deepened: replaced the retired GIST header; read the deepened anchor and the named adjacent rows;
expanded the genre into a route-by-owning-situation taxonomy; added the exact reciprocal collision
fixtures for building control, construction jobs, materials delivery, site safety, block/tenancy,
household property, insurance, corporate filings, and Photos; added three JSON fixtures covering
batch conformity, recurring examination, and corporate registry certificates; closed the Reading
Inbox, Receipts and Confirmations, Reference Clips, and Unsupported or Encrypted escape routes; and
converted the broad routing question into NJ-CP-CC-1.

The result remains a refusal, now with every plausible certificate type given a surviving owner or a
named residual. Nothing depends on this node firing.
