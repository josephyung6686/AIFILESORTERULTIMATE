# Research memo — `creative.interior-design`

Depth: **FULL R1b DEPTH (ratified J-DEPTH, 2026-08-24)**

## Verdict

Stand the template. Interior design is not a node merely because it uses drawings, renders, rooms,
materials, styles or CAD extensions. It earns a template when the evidence describes a physical-space
commission or project moving through a distinctive design-to-installation lifecycle: brief and survey,
concept, spatial/technical design, schedules and specification, procurement, site work, and
installation/handover. That lifecycle changes recognition and grouping from the creative schema's
general making record. It may also overlap with construction/property material when a fit-out is part
of a larger build. The row writes no fields and recommends no dimensions because `creative` is a
placeholder schema with `fields: []`.

The node test:

1. **Detection.** A room/space brief tied to measured survey, drawings, schedules, specification,
   supplier/procurement records and installation or handover evidence is a coherent structural signal.
   A lone render, moodboard, invoice or room photograph is not. The decisive evidence is the chain and
   cross-reference, not style language or an extension.
2. **Dimensions.** The inherited schema declares no legal field rows. The physical property, room,
   style, material and lifecycle stage are values or observations until a shared canonical vocabulary
   is adjudicated. A future order such as project/commission → property/site → stage → room/artifact
   is useful, but putting any of those unlicensed keys in `dimension_order` would create a destination
   level no fact can fill. The current honest order is empty.
3. **Privacy.** Addresses, budgets, access arrangements, security layouts, supplier pricing and
   photographs of occupied homes/workplaces can be sensitive. This posture differs operationally from
   a generic isolated image or public portfolio, but it is the creative/property context—not a new
   interior-specific handling class—that supplies the rule. `potentially_sensitive` is retained.

This is therefore a narrower template inside the creative schema, with an explicit construction/property
boundary. It does not turn `interior`, `residential`, `hospitality`, `minimalist`, `Japandi`, `marble`,
`oak`, `kitchen`, or any furniture/product type into nodes.

## Sources and comparison set

I used the binding brief and stamped assignment from `python3 planning/domains/dispatch/make_prompt.py
creative.interior-design`, `planning/00-database-agent-product-design.md`, `01-product-design-structured.md`,
`planning/domains/_CONTRACT.md`, `CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `canonical_fields.json`, the
roster, and the `creative` schema row. The schema's default is the general making record: one named
piece of work moving through revisions toward delivery, showing or publication, with linked assets,
layers/artboards, briefs, version families and handoff sets. I compared the row with `career`, `code`,
`photos`, `career.portfolio-work-samples`, `code.software-project`, `construction_property`,
`construction_property.construction-project`, `finance.household-property`, and the landed creative
client-engagement and deliverable-handoff rows.

The design supports purpose-coherent groups even when formats differ, and says that an extension is a
routing signal rather than an assumption about meaning. Those principles are why this memo treats a
specification/procurement/install chain as evidence, but rejects `.dwg`, `room`, `style`, `FINAL`, and
an address as facts by themselves. The concrete files below are practitioner-style fixtures and argued
inferences, not claims that these exact files exist in a universal corpus.

## Bottom-up file investigation

### 1. `Riverside Apartment - Interior Brief.docx`

The labelled heading, room list, constraints, budget narrative and requested outcomes make this a
purpose-bearing brief. It can seed a creative project group and a client-engagement interpretation if
role-bearing language identifies the counterparty. The apartment address and organisation names remain
observations until a resolver distinguishes subject property, mailing address, designer, client and
owner. A brief can request furniture, lighting, joinery, artwork and contractor work together; its
content is not proof of a particular style. If no project neighbourhood is accepted, it is an
Independent Record.

### 2. `Riverside_Apt_measured-survey_existing.dwg`

CAD layers for walls, openings and dimensions, room labels and a survey date establish measured-space
evidence. They do not establish that the designer authored the existing conditions or that an address in
the title block is a validated property fact. A same-stem PDF and subsequent plan strengthen group
membership without copying facts to sparse files. An unreadable proprietary drawing remains indexed but
unreadable and falls to Unsupported or Encrypted when no group is accepted.

### 3. `Riverside_Apt_Stage-4_Finishes-and-Fixtures.xlsx`

This is a populated specification/schedule, not a blank template: room/location, item, finish,
manufacturer, product reference, quantity, revision and status columns co-occur. It is one of the
strongest interior-specific forms because it translates a spatial design into procurement-ready
choices. It does not prove that anything was ordered, delivered or installed. Product references are
observations; a material/style value must not become a field or folder level. If detached from any design
or property context it is a durable Independent Record.

### 4. `Riverside_Apt_kitchen_joinery_approved.pdf`

Dimensioned elevations and sections, joinery tags pointing to a schedule, and an issue/approval block
are technical design evidence. “Approved” is an observed status token, not proof of construction. This
file belongs in an interior project when the drawing set and specification cohere. It can sit in a larger
construction project when contract/site administration is also evidenced. Approval does not convert it
into a legal instrument or a property transaction record.

### 5. `Riverside_Apt_supplier-quote_lighting.eml`

The email has a quotation attachment, item references matching the lighting schedule, lead-time
discussion and a project reference. That is procurement evidence and a candidate group member. The quote
is not an order, invoice, payment confirmation or installation certificate. The supplier name is not the
client; it is a role-bearing counterparty only when the email text supports that role. Detached from the
design chain it belongs in Review Later, or in a transactional residual once its purpose is clear.

### 6. `Riverside_Apt_installation-week-03.jpg`

The image may show site progress and carry EXIF or a capture date, but pixels alone cannot establish
project, room, completion, contractor or property. A captioned progress report or adjacent issue record
can support membership; the graph must not copy project facts onto the image. Photos can independently
hold capture metadata. Without a design/install relationship this is an One-Off Image, not interior
design evidence.

### 7. `Riverside_Apt_handover-pack.zip`

The manifest and cover note list as-built drawings, room schedules, manuals, warranties and completion
photographs for handover. This is a strong lifecycle endpoint: the package is purpose-coherent across
formats and records the installed space. Archive inspection must not copy member names or claims to
individual files. A file called `handover-pack.zip` with no manifest, recipient or project context is
only a possible archive and falls to Unsupported or Encrypted or Review Later.

### 8. `Interior Concepts - Oak House Portfolio.pdf`

Rendered rooms and polished captions look interior-specific, but case-study language and absence of
editable sources, schedules, procurement trail or site issue context point to a career work sample. The
same render may be exported from an active project; purpose and neighbourhood decide. The portfolio file
is a collision with `career.portfolio-work-samples`, not automatic evidence of an active commission.

### 9. `Oak House - renovation cost tracker.xlsx`

Totals, payment status and a property heading may belong to household-property administration. It is not
an interior design project merely because the spending is on renovation. A cost tracker can be an
additional member of a design group when the design/specification relation is explicit, while its finance
facts remain its own. Otherwise `finance.household-property` owns the purpose and the file is not this
template.

### 10. `Showroom_furniture_catalogue_2026.pdf`

Product images, dimensions and prices are a supplier catalogue. There is no room schedule, project
reference, selection mark, quote request or commission. It is the cleanest false positive for a material
and furniture-driven detector. It belongs in Reading Inbox or Reference Clips. A catalogue can become a
project member only through an explicit selection/procurement relation, not because a designer downloaded
it during a session.

## Files considered and rejected

The following signals were deliberately rejected as sufficient activation: a room name; street address;
style words such as “Japandi” or “minimal”; a product or manufacturer name; a material swatch; a colour
code; an image of a finished room; a render; a `.dwg`, `.rvt`, `.skp`, `.3dm`, `.pdf`, `.xlsx` or `.jpg`
extension; a title-block “FINAL” or “APPROVED”; an invoice or purchase order; a contractor or designer
name; a furniture catalogue; a blank specification template; a calendar appointment called “site visit”;
and a folder called `Renovation`. Each may support retrieval or group review, but none distinguishes an
interior project from a construction record, a home expense, a portfolio, a downloaded reference or a
software repository.

An archive is also rejected when its only evidence is a filename. A mixed archive with a manifest,
cover note, project reference and linked design/specification/install members is different: its purpose
coherence is the activation evidence, while members retain their own observations.

## Default and node distinction

The creative default already catches authored working files, linked assets, layers/artboards, revisions,
briefs and handoff sets. Interior design shares all of those structures. Its additional structural
signal is the physical-space lifecycle and its translation chain: measured conditions become a room/space
plan; design decisions become schedules/specifications; specifications become supplier and purchasing
records; site evidence becomes installation, snagging, as-built and handover records. The chain is
cross-format and purpose-coherent. A graphic poster, illustration or identity system may have briefs,
layers and deliverables but does not ordinarily have room/space measurement, fixture/finish schedules,
site installation and practical handover evidence.

This is an inference from the design's named creative-project concept and its purpose-coherence and
grouping rules, not a claim that the design document names “interior design” as a built-in schema. The
row therefore uses `provenance: inference`, leaves `design_cite` null, and preserves the fieldless launch
contract.

## Reciprocal boundaries

### `construction_property.construction-project`

Shared fixture: `Riverside_Apt_kitchen_joinery_approved.pdf` and the handover pack. Construction/property
owns build contracts, site administration, programme, permits, trades, commercial claims, compliance and
the broader physical works when those signals are present. Interior design owns the space brief,
concept/technical design, finish and fixture decisions, supplier selection and the design-to-installation
handover chain. A fit-out package may legitimately be both schemas when both purposes are evidenced; a
room schedule does not by itself activate the construction template, and a site contract does not by
itself make every construction document an interior design record.

### `finance.household-property`

Shared fixture: `Oak House - renovation cost tracker.xlsx` and an improvement invoice. Finance owns
household property administration, expenses, tax, warranties and payment/account records. Interior
design requires a design/specification/procurement/install relation. A property address and renovation
spend cannot activate this row. Conversely, a selected item in a schedule may remain an interior member
even when its paid invoice also supports Finance; facts are not copied across schemas.

### `career.portfolio-work-samples`

Shared fixture: `Interior Concepts - Oak House Portfolio.pdf`. Career owns a presentation demonstrating
the maker's work, skills or outcomes. Interior owns active project sources, issues, schedules, supplier
correspondence and site/handover records. A finished render can be exported into both contexts only when
each purpose is evidenced; a portfolio case study must not be treated as a live commission merely because
it depicts a room.

### `photos`

Shared fixture: `Riverside_Apt_installation-week-03.jpg`. Photos owns capture date, camera and event
metadata. Interior owns the project relation and installation-stage meaning when supported by captions,
reports or project neighbours. EXIF does not prove installation; lack of EXIF does not prove screenshot.
The same bytes may carry photo facts and belong to an interior group, but sparse images do not inherit
room, property or completion facts from their neighbours.

### `code.software-project`

Shared fixture: a BIM/CAD model export or an asset under a repository's `models/` directory. Code owns
repository manifests, source tree, build/dependency and executable-project structure. Interior owns a
standalone issued design set or model participating in the space lifecycle. A file extension and room
labels cannot override a repository structure; conversely, a model delivered with schedules and
handover evidence is not code merely because it can be opened by software.

### `creative.client-engagement` and `creative.deliverable-handoff`

Client engagement owns the counterparty relationship across correspondence, briefs, approvals and
multiple works; handoff owns package/recipient/transmission structure. Interior may be nested in either
workflow, but its physical-space lifecycle remains the distinguishing situation. A signed brief can
support client engagement without proving interior design; a handover archive can support deliverable
handoff without room-specific design evidence. No edge is authored to these siblings because this row's
activation is a cross-template purpose overlap rather than a mutex collision and their reciprocal rows
must settle any edge contract together.

## Fields, values, edges and residual coverage

`fields: []` and `proposed_fields: []` are deliberate. The row must not mint `property`, `site`, `room`,
`style`, `material`, `finish`, `supplier`, `trade`, `phase` or `installation_stage`. `project`, `stage`
and `artifact_type` are already creative proposals/values, but this placeholder cannot legalise them.
Interior, hospitality, residential, kitchen and style terms belong in work-type or runtime vocabulary.

No `also_holds_with` edge is written: the schema pair is not being adjudicated here, and a template-level
relationship is not a schema-level edge. Collisions are recorded for career, code, photos, construction
project and household property because the same bytes can be mistaken for those situations. Heterogeneous
design/handover packs should remain multi-purpose where both schemas independently activate, not be forced
into a mutex.

When activation fails, durable briefs, schedules and standalone records fall through to Independent
Records; unresolved quotes, emails and ambiguous project material to Review Later; isolated site or room
images to One-Off Images; downloaded visual/product references to Reference Clips or Reading Inbox; and
unreadable design archives to Unsupported or Encrypted. These are safe residuals, not a new interior
taxonomy.

## NEEDS-JOSEPH

**NJ-INTERIOR-1 — shared physical subject key.** Should future schemas adopt one `property`, `venue` or
`site` join handle?

- Recommended: one shared property/site vocabulary with role-bearing validation and no address-only
  inference, enabling creative, construction_property, photos and finance retrieval to meet safely.
- Alternative: keep physical subject group-only and never expose it as a canonical field, avoiding a
  sensitive destination dimension but weakening cross-domain retrieval.
- Alternative: split household property and commissioned venue, which better reflects roles but duplicates
  vocabulary and creates a boundary Joseph must maintain.

**NJ-INTERIOR-2 — portfolio overlap.** Should a completed interior case study also hold the active project
when the same export is reused? Option A: allow multi-membership only when each purpose has evidence;
Option B: make career presentation a collision and keep only source/handover bytes in the project.
This row does not resolve the product policy.

## What changed in this pass

- Established a standing template instead of refusing the id, based on the physical-space lifecycle and
  its design → specification → procurement → installation/handover chain.
- Kept the launch row fieldless and dimensionless; space, style, room, material, property and stage are
  explicitly values/observations or future shared-vocabulary questions.
- Added ten concrete fixtures, including catalogue, portfolio, household-cost and archive false positives.
- Recorded reciprocal boundaries with construction/property, Finance, career, photos and code.
- Preserved sensitivity and residual routes without inventing handling classes or detector thresholds.

## Validation and claims

The paired JSON parses, uses the stamped id and `schema_id`, has the universal key set, has ten file
examples with allowed source types, keeps `fields` and `proposed_fields` empty, uses only roster ids in
collisions, uses only residual names in `falls_through_to`, and agrees with this memo on standing verdict,
fieldlessness, empty dimensions, lifecycle recognition, sensitivity and NEEDS-JOSEPH items. No other file
was edited.

**END — creative.interior-design — STANDS**
